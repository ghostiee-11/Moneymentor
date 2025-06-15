# tax_tool_server.py
import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL_NAME = 'llama3-8b-8192' # Or 'llama3-70b-8192'
SERVER_PORT = 5004
# Allow requests from your frontend's origin (e.g., http://127.0.0.1:5500 if using Live Server)
# *** UPDATE THIS ***
ALLOWED_ORIGIN = "http://127.0.0.1:3000"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(funcName)s] %(message)s')

# --- Validation ---
if not GROQ_API_KEY:
    logging.error("FATAL: GROQ_API_KEY not found. Exiting.")
    exit(1)

# --- Flask App Setup ---
app = Flask(__name__)
CORS(app, resources={r"/get-tax-strategy": {"origins": ALLOWED_ORIGIN}}) # Only allow POST to this endpoint from the specified origin

# --- Groq Client ---
try:
    groq_client = Groq(api_key=GROQ_API_KEY)
    logging.info("Groq client initialized successfully.")
except Exception as e:
    logging.error(f"Failed to initialize Groq client: {e}")
    groq_client = None # Handle case where initialization fails

# --- System Prompt ---
# This prompt guides the AI on its role and limitations regarding Indian tax strategy.
SYSTEM_PROMPT = """
You are an AI assistant specializing in providing *general* Indian Income Tax strategy ideas and information based on the user's input.

**IMPORTANT DISCLAIMER:** You are NOT a qualified tax advisor. The information and strategies you provide are for informational and educational purposes only. They should NOT be considered professional tax advice. Users must consult with a qualified tax professional or chartered accountant (CA) for advice specific to their personal financial situation. Tax laws are complex and subject to change.

**Your Task:**
Based on the user's provided information (like income, age, basic investments/expenses, etc.), suggest relevant tax-saving strategies and options available under Indian tax laws. Explain common deductions (like Section 80C, 80D, HRA, etc.), touch upon differences between old and new tax regimes where relevant, and mention typical tax-saving instruments (like PPF, ELSS, NPS, health insurance, etc.).

**Response Guidelines:**
- Start with the disclaimer clearly.
- Address the user's input and acknowledge the context (e.g., "Based on your approximate income...").
- Suggest relevant strategies and deductions based on the input. Explain *what* they are briefly.
- Mention common investment options for tax saving.
- Avoid calculating specific tax amounts.
- Keep the language clear and easy to understand, but retain accuracy regarding section names/instrument types.
- Conclude by reiterating the importance of consulting a professional tax advisor.
"""

# --- API Endpoint ---
@app.route('/get-tax-strategy', methods=['POST'])
def get_tax_strategy():
    """
    Receives user's tax information and returns AI-generated strategy.
    """
    if groq_client is None:
        logging.error("Groq client is not initialized.")
        return jsonify({"error": "AI service not available."}), 503

    if not request.is_json:
        logging.warning("Received non-JSON request.")
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Extract data with validation
    income = data.get('income')
    age = data.get('age')
    details = data.get('details', '') # Optional details

    if income is None or age is None:
        logging.warning("Missing income or age in request.")
        return jsonify({"error": "Missing required information (income and age)."}), 400

    # Basic type/value validation
    try:
        income = float(income)
        age = int(age)
        if income < 0 or age < 0: raise ValueError("Negative values not allowed")
    except (ValueError, TypeError):
        logging.warning(f"Invalid income or age format: income={income}, age={age}")
        return jsonify({"error": "Income and age must be valid numbers."}), 400

    logging.info(f"Received request for tax strategy: Income={income}, Age={age}")

    # Construct the user message
    user_message_content = f"""
Here is my information for Indian tax strategy ideas:
Approximate Annual Income: ₹{income:,.0f}
Age: {age} years
Other relevant investments/expenses/details: {details if details else 'Not specified.'}

Please provide general tax-saving strategies based on this.
"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message_content}
    ]

    try:
        logging.info(f"Calling Groq API with model: {GROQ_MODEL_NAME}")
        chat_completion = groq_client.chat.completions.create(
            messages=messages,
            model=GROQ_MODEL_NAME,
            temperature=0.5, # Adjust temperature for creativity vs focus
            max_tokens=1500 # Limit response length
        )
        response_content = chat_completion.choices[0].message.content
        logging.info("Received response from Groq.")
        return jsonify({"strategy": response_content.strip()})

    except Exception as e:
        logging.error(f"Error calling Groq API: {e}", exc_info=True)
        return jsonify({"error": "Sorry, an error occurred while generating the tax strategy."}), 500

# --- Run Server ---
if __name__ == '__main__':
    # Use host='0.0.0.0' to make it accessible externally if needed
    logging.info(f"Starting Flask server on port {SERVER_PORT}... Allowing requests from origin: {ALLOWED_ORIGIN}")
    # debug=True should be False in production
    app.run(debug=True, port=SERVER_PORT)