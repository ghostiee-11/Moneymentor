import os
import yfinance as yf
from flask import Flask, render_template, jsonify, request
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# --- Groq Chatbot Setup ---
groq_api_key = os.getenv('GROQ_API_KEY')
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables.")

try:
    groq_client = Groq(api_key=groq_api_key)
except Exception as e:
    print(f"Error initializing Groq client: {e}")
    groq_client = None # Handle case where initialization fails

# --- Tickers for Market Data ---
# Using yfinance symbols
TICKERS = {
    "Nifty 50": "^NSEI",
    "Sensex": "^BSESN",
    "Bank Nifty": "^NSEBANK",
    "Bitcoin (BTC-USD)": "BTC-USD",
    "Ethereum (ETH-USD)": "ETH-USD",
}

# --- Flask Routes ---

@app.route('/')
def index():
    """Renders the main dashboard HTML page."""
    return render_template('index.html', tickers=TICKERS.keys())

@app.route('/get_realtime_price/<name>')
def get_realtime_price(name):
    """Fetches and returns the current price for a given ticker name."""
    ticker_symbol = TICKERS.get(name)
    if not ticker_symbol:
        return jsonify({"error": "Ticker not found"}), 404

    try:
        ticker = yf.Ticker(ticker_symbol)
        # Using fast_info for quicker access to current price data
        # Fallback to info if fast_info is not available or missing data
        try:
            data = ticker.fast_info
            price = data.last_price if data.last_price is not None else data.current_price
        except Exception:
             data = ticker.info
             price = data.get('currentPrice') or data.get('regularMarketPrice')


        if price is not None:
             # Determine currency/unit - simplified logic
            currency = data.get('currency', '').upper()
            if currency == 'INR':
                 unit = '₹'
            elif currency == 'USD':
                 unit = '$'
            else:
                 unit = currency # Use currency code if not INR/USD

            return jsonify({"price": price, "unit": unit})
        else:
            return jsonify({"error": "Price data not available"}), 404

    except Exception as e:
        print(f"Error fetching real-time price for {ticker_symbol}: {e}")
        return jsonify({"error": "Could not fetch data", "details": str(e)}), 500


@app.route('/get_historical_data/<name>')
def get_historical_data(name):
    """Fetches and returns historical closing prices for charting."""
    ticker_symbol = TICKERS.get(name)
    if not ticker_symbol:
        return jsonify({"error": "Ticker not found"}), 404

    try:
        # Fetch data for the last 30 days
        history = yf.Ticker(ticker_symbol).history(period="30d")

        if history.empty:
             return jsonify({"error": "No historical data available"}), 404

        # Extract dates and closing prices
        dates = history.index.strftime('%Y-%m-%d').tolist()
        closes = history['Close'].tolist()

        return jsonify({"dates": dates, "closes": closes})

    except Exception as e:
        print(f"Error fetching historical data for {ticker_symbol}: {e}")
        return jsonify({"error": "Could not fetch historical data", "details": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Handles chatbot requests."""
    if groq_client is None:
         return jsonify({"error": "Chatbot service not available"}), 503

    data = request.json
    user_message = data.get('message')

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        # Define the model and a system prompt
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful market analysis assistant. Answer questions about the financial markets, indices, or cryptocurrencies based on general knowledge. Keep your responses concise and informative. Do not provide real-time data, as the data is provided by the dashboard itself."
                },
                {
                    "role": "user",
                    "content": user_message,
                }
            ],
            model="llama3-8b-8192", # Or "llama3-70b-8192" for a larger model
            temperature=0.7, # Adjust creative temperature
            max_tokens=500, # Limit response length
            top_p=1,
            stream=False,
            stop=None,
        )

        assistant_response = chat_completion.choices[0].message.content

        return jsonify({"response": assistant_response})

    except Exception as e:
        print(f"Error communicating with Groq API: {e}")
        return jsonify({"error": "Could not get response from chatbot", "details": str(e)}), 500

# --- Run the App ---
if __name__ == '__main__':
    # Use debug=True for development. In production, use a production WSGI server.
    app.run(debug=True)