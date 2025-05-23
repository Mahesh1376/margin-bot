import logging
from flask import Flask, request, jsonify
import json
import os
import hmac
import hashlib
import requests
from dotenv import load_dotenv
import time
load_dotenv()  # Load variables from .env file

app = Flask(__name__)

# Load sensitive info
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

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

logging.basicConfig(level=logging.INFO)
@app.route('/', methods=['GET'])
def home():
    return "🚀 CoinDCX Margin Bot is Running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("🔔 Webhook received:", data)
    print(f"📩 TradingView Alert: {data}")

    symbol = data.get("symbol")
    side = data.get("side")
    qty = data.get("qty")

    if not symbol or not side or not qty:
        return jsonify({"status": "error", "message": "Missing data"}), 400

    # CoinDCX margin endpoint
    url = "https://api.coindcx.com/exchange/v1/margin/create_order/"

    # Convert qty to float
    try:
        qty = float(qty)
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid qty"}), 400

    # Create order params
    payload = {
        "symbol": symbol,
        "side": side.upper(),         # "LONG" or "SHORT"
        "quantity": qty,
        "order_type": "market",
        "leverage": 5,
        "position_side": "BOTH"       # Cross margin mode
    }

    timestamp = int(round(time.time() * 1000))
    body = json.dumps(payload)

    signature = hmac.new(
        API_SECRET.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": API_KEY,
        "X-AUTH-SIGNATURE": signature,
        "X-AUTH-TIMESTAMP": str(timestamp)
    }

    try:
        response = requests.post(url, data=body, headers=headers)
        print("📈 CoinDCX response:", response.json())

        return jsonify({
            "status": "success",
            "message": "Trade executed",
            "coindcx_response": response.json()
        })

    except Exception as e:
        print("❌ Error placing order:", e)
        return jsonify({"status": "error", "message": str(e)})
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

