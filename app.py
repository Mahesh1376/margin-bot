import logging
from flask import Flask, request, jsonify
import json
import os
import hmac
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

app = Flask(__name__)

# Load sensitive info
API_KEY = os.getenv('c8a90d84e6c1098d453f216fdb0f6480d7b3cad202b68cc3')
API_SECRET = os.getenv('1b7888990f5090c993a4cc0ce89723462fa89982ff7dcc652adad5c6a064f62c')
print("API_SECRET is:", API_SECRET)

HEADERS = {
    'Content-Type': 'application/json',
    'X-AUTH-APIKEY': API_KEY,
}

COINDCX_BASE = 'https://api.coindcx.com'

def place_order(side, symbol, quantity, leverage):
    path = "/exchange/v1/margin/create_order"
    body = {
        
        "order_type": "market",
        "leverage": leverage,
        "mode": "cross"
    }

    payload = json.dumps(body)
    signature = hmac.new(
        API_SECRET.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()

    HEADERS['X-AUTH-SIGNATURE'] = signature

    response = requests.post(COINDCX_BASE + path, headers=HEADERS, data=payload)
    print(f"[DEBUG] Order response: {response.text}")
    return response.json()

logging.basicConfig(level=logging.DEBUG)
@app.route('/', methods=['GET'])
def home():
    return "🚀 CoinDCX Margin Bot is Running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("🔔 Webhook received with data:", data)

    symbol = data.get("symbol")
    side = data.get("side")
    qty = data.get("qty")

    print(f"➡️ Placing order: {side.upper()} {qty} units of {symbol}")

    # Simulate trading logic (for now)
    return jsonify({"status": "success", "message": "Trade executed"})

    if not symbol or not side or not qty:
       return jsonify({'status': 'error', 'message': 'Missing parameters'}), 400

    print(f"Received trade request: {symbol}, {side}, {qty}")
    return jsonify({'status': 'success', 'message': 'Trade executed'})
    try:
        # Here, you can add your logic for placing the order with CoinDCX
        if side.lower() == "long":
            # Execute long trade logic (buy)
            app.logger.info(f"Placing long order for {qty} of {symbol}")
            # Add code to place long order via CoinDCX API (You can use the CoinDCX API wrapper here)
        
        elif side.lower() == "short":
            # Execute short trade logic (sell)
            app.logger.info(f"Placing short order for {qty} of {symbol}")
            # Add code to place short order via CoinDCX API
        
        else:
            app.logger.error("Invalid side provided. Must be 'long' or 'short'.")
            return jsonify({"message": "Invalid side, must be 'long' or 'short'", "status": "error"}), 400
        
        # Step 4: Return success response
        return jsonify({"message": "Order placed successfully", "status": "success"}), 200
    
    except Exception as e:
        app.logger.error(f"Error processing webhook: {e}")
        return jsonify({"message": "Error processing webhook", "status": "error"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)  # Make sure to use the correct port for Render deployment
