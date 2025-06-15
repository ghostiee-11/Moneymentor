from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import math
import random # For a slightly varied market context

app = Flask(__name__)
# Allow requests from any origin during development.
# For production, you would restrict this: CORS(app, origins=["https://yourdomain.com"])
CORS(app)

# --- Mock Data and Logic ---

# Estimated annual returns based on risk profile (as decimals)
# These are simplified for demonstration
ESTIMATED_ANNUAL_RETURNS = {
    "Low": 0.05,  # 5% p.a.
    "Medium": 0.08, # 8% p.a.
    "High": 0.12  # 12% p.a.
}

# Example Asset Allocation based on risk profile (as decimals summing to ~1)
# Using 5 asset classes as hinted by the JS comment
ASSET_ALLOCATIONS = {
    "Low": {
        "Large Cap Stocks": 0.40,
        "Bonds": 0.50,
        "Gold": 0.10,
        "Mid/Small Cap Stocks": 0.00, # Not in low risk
        "Digital Assets": 0.00       # Not in low risk
    },
    "Medium": {
        "Large Cap Stocks": 0.50,
        "Mid/Small Cap Stocks": 0.15,
        "Bonds": 0.25,
        "Gold": 0.05,
        "Digital Assets": 0.05       # Small allocation
    },
    "High": {
        "Large Cap Stocks": 0.30,
        "Mid/Small Cap Stocks": 0.30,
        "Bonds": 0.05,             # Very low bond allocation
        "Gold": 0.10,
        "Digital Assets": 0.25       # Significant allocation
    }
}

# Simulated Market Context Data (simplified)
# Prices will slightly vary each time for demo
def get_simulated_market_data():
    # Base prices (approximate INR)
    base_nifty = 24718.60
    base_sensex = 81118.60
    base_bitcoin = 9061245.83 # Example price in INR
    base_ethereum = 217725.34 # Example price in INR
    base_gold = 102400.00 

    # Add some minor random fluctuation (+/- 1% max)
    fluctuation = lambda base: base * (1 + (random.random() - 0.5) * 0.02)

    return {
        "assets": {
            "Indices": {
                "NIFTY": {"name": "Nifty 50", "current_price": fluctuation(base_nifty), "currency": "INR"},
                "SENSEX": {"name": "Sensex", "current_price": fluctuation(base_sensex), "currency": "INR"}
            },
            "Crypto": {
                "BTC": {"name": "Bitcoin", "current_price": fluctuation(base_bitcoin), "currency": "INR"},
                "ETH": {"name": "Ethereum", "current_price": fluctuation(base_ethereum), "currency": "INR"}
            },
            "Gold": {
                "GOLD": {"name": "Gold (10g)", "current_price": fluctuation(base_gold), "currency": "INR"}
            }
        }
    }

# --- API Endpoints ---

@app.route('/market/context', methods=['GET'])
def market_context():
    """
    Provides a snapshot of current market conditions.
    """
    print("Received request for market context")
    time.sleep(2) # Simulate network delay
    data = get_simulated_market_data()
    print("Sending market context response")
    return jsonify(data)

@app.route('/goal-recommendation', methods=['POST'])
def goal_recommendation():
    """
    Receives goal parameters and generates an investment plan.
    """
    print("Received request for goal recommendation")
    time.sleep(3) # Simulate processing time

    data = request.get_json()

    # --- Input Validation ---
    if not data:
        print("Error: No JSON data received")
        return jsonify({"detail": "Invalid input: No JSON data provided."}), 400

    goal_name = data.get('goal_name')
    risk_profile = data.get('risk_profile')
    goal_duration_years = data.get('goal_duration_years')
    goal_target_amount = data.get('goal_target_amount')
    preferred_frequency = data.get('preferred_frequency') # This is used for display order/log button, but we calculate ALL periods

    if not all([goal_name, risk_profile, goal_duration_years is not None, goal_target_amount is not None, preferred_frequency]):
        print(f"Error: Missing data - goal_name={goal_name}, risk_profile={risk_profile}, duration={goal_duration_years}, target={goal_target_amount}, freq={preferred_frequency}")
        return jsonify({"detail": "Invalid input: Missing required fields."}), 400

    try:
        goal_duration_years = int(goal_duration_years)
        goal_target_amount = float(goal_target_amount)
    except (ValueError, TypeError):
        print(f"Error: Invalid number format - duration={goal_duration_years}, target={goal_target_amount}")
        return jsonify({"detail": "Invalid input: Duration and target amount must be numbers."}), 400

    if goal_duration_years <= 0:
         print(f"Error: Duration must be positive - {goal_duration_years}")
         return jsonify({"detail": "Invalid input: Goal duration must be at least 1 year."}), 400

    if goal_target_amount <= 0:
         print(f"Error: Target amount must be positive - {goal_target_amount}")
         return jsonify({"detail": "Invalid input: Goal target amount must be greater than 0."}), 400

    if risk_profile not in ESTIMATED_ANNUAL_RETURNS:
        print(f"Error: Invalid risk profile - {risk_profile}")
        return jsonify({"detail": "Invalid input: Invalid risk profile selected."}), 400

    if preferred_frequency not in ['monthly', 'quarterly', 'yearly']:
        print(f"Error: Invalid frequency - {preferred_frequency}")
        return jsonify({"detail": "Invalid input: Invalid investment frequency selected."}), 400

    # --- Investment Calculation ---
    estimated_annual_return = ESTIMATED_ANNUAL_RETURNS.get(risk_profile)
    asset_allocation = ASSET_ALLOCATIONS.get(risk_profile)

    if estimated_annual_return is None or asset_allocation is None:
         # This should not happen with the checks above, but as a safeguard
         print(f"Internal Error: Could not retrieve data for risk profile {risk_profile}")
         return jsonify({"detail": "Internal server error: Could not process risk profile."}), 500

    required_investment_periods = []

    # Calculate required periodic investment for different frequencies
    periods_map = {
        'monthly': 12,
        'quarterly': 4,
        'yearly': 1
    }

    for period_name, periods_per_year in periods_map.items():
        total_periods = goal_duration_years * periods_per_year
        rate_per_period = estimated_annual_return / periods_per_year
        required_total_investment_this_period = 0
        breakdown_this_period = {}

        try:
            if rate_per_period == 0:
                # Simple division if no return
                if total_periods > 0:
                    required_total_investment_this_period = goal_target_amount / total_periods
            else:
                # Annuity formula: P = FV * [r / ((1 + r)^n - 1)]
                denominator = (1 + rate_per_period)**total_periods - 1
                if denominator != 0:
                    required_total_investment_this_period = goal_target_amount * (rate_per_period / denominator)
                # else: required_total_investment_this_period remains 0 (e.g. target 0, or math issue)

            # Ensure investment is non-negative and sensible (e.g. not infinity)
            if not math.isfinite(required_total_investment_this_period) or required_total_investment_this_period < 0:
                 required_total_investment_this_period = 0

            # Calculate breakdown if total investment is positive
            if required_total_investment_this_period > 0.001: # Use a small threshold
                 for asset, percentage in asset_allocation.items():
                     breakdown_this_period[asset] = required_total_investment_this_period * percentage

            required_investment_periods.append({
                 "period": period_name,
                 "required_total_investment": round(required_total_investment_this_period, 2), # Round for currency display
                 "breakdown": {asset: round(amount, 2) for asset, amount in breakdown_this_period.items()} # Round breakdown amounts
            })

        except Exception as e:
            print(f"Calculation error for {period_name}: {e}")
            # Optional: Log the error but continue for other periods

    # --- Generate Explanation ---
    # A simple static/templated explanation
    explanation = f"""
Based on your goal of "{goal_name}" and a {risk_profile} risk profile over {goal_duration_years} years targeting {goal_target_amount:,.2f} INR, your estimated annual portfolio return is {estimated_annual_return*100:.1f}%.

To achieve this goal, we recommend the following asset allocation:
"""
    # Add allocation details to explanation
    for asset, percentage in asset_allocation.items():
         if percentage > 0:
              explanation += f"\n- **{asset}**: {(percentage * 100):.0f}%"

    explanation += f"""

This allocation balances growth potential with your stated risk comfort level. The recommended periodic investments are calculated to potentially reach your target amount by the end of the duration, assuming the estimated rate of return. Remember, returns are estimates and not guaranteed.

Here is the required investment per period:
"""
    if required_investment_periods:
        for period_data in required_investment_periods:
            total_amount = period_data['required_total_investment']
            explanation += f"\n- **{period_data['period'].capitalize()}**: {total_amount:,.2f} INR total."
            if period_data['breakdown']:
                 explanation += " Breakdown:"
                 # Sort breakdown for consistent explanation text
                 sorted_breakdown = sorted(period_data['breakdown'].items(), key=lambda item: item[1], reverse=True)
                 for asset, amount in sorted_breakdown:
                     explanation += f" {asset}: {amount:,.2f} INR;"
                 explanation = explanation.rstrip(';') + '.' # Clean up last entry

    explanation += """

Consider investing regularly according to the breakdown for your preferred frequency. Market conditions can fluctuate, and periodic review of your plan may be beneficial. This plan is based on current data and is not financial advice.
"""

    # --- Construct Response ---
    response_data = {
        "goal_name": goal_name,
        "risk_profile": risk_profile,
        "goal_duration_years": goal_duration_years,
        "goal_target_amount": goal_target_amount,
        "preferred_frequency": preferred_frequency,
        "estimated_portfolio_return": estimated_annual_return,
        "allocation": asset_allocation, # Overall allocation percentages
        "required_investment_periods": required_investment_periods, # Breakdown by period amount
        "explanation": explanation.strip() # Remove leading/trailing whitespace
    }

    print("Sending goal recommendation response")
    return jsonify(response_data)

# --- Run Server ---
if __name__ == '__main__':
    # Use host='0.0.0.0' to make it accessible externally if needed,
    # but for local development '127.0.0.1' or default is fine.
    print("Starting Flask server on http://127.0.0.1:5002")
    app.run(debug=True, port=5002)