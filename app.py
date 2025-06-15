from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from groq import Groq

app = Flask(__name__)
CORS(app)

# Load Groq API key from env (set it in Render)
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ========================================
# 🔹 Chatbot using Groq (LLaMA3-8B)
# ========================================
@app.route("/chatbot", methods=["POST"])
def chatbot():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    try:
        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful financial assistant."},
                {"role": "user", "content": user_input},
            ]
        )
        reply = response.choices[0].message.content.strip()
        return jsonify({"response": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ========================================
# 🔹 Goal Setting (from goal.py)
# ========================================
@app.route('/goal', methods=['POST'])
def goal():
    data = request.json
    try:
        income = float(data['income'])
        expenses = float(data['expenses'])
        target = float(data['target'])
        months = int(data['months'])

        savings = income - expenses
        monthly_goal = target / months

        status = "On Track" if savings >= monthly_goal else "Increase Savings"

        return jsonify({
            "monthly_goal": round(monthly_goal, 2),
            "current_savings": round(savings, 2),
            "status": status
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ========================================
# 🔹 Tax Calculator (from tax_tool_server.py)
# ========================================
@app.route("/tax", methods=["POST"])
def tax_calculator():
    data = request.json
    try:
        income = float(data["income"])
        deductions = float(data["deductions"])

        taxable_income = max(income - deductions, 0)
        tax = 0.0

        if taxable_income <= 250000:
            tax = 0
        elif taxable_income <= 500000:
            tax = (taxable_income - 250000) * 0.05
        elif taxable_income <= 1000000:
            tax = 12500 + (taxable_income - 500000) * 0.2
        else:
            tax = 112500 + (taxable_income - 1000000) * 0.3

        return jsonify({
            "taxable_income": taxable_income,
            "estimated_tax": round(tax, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ========================================
# 🔹 Render Port Binding
# ========================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
