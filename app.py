from flask import Flask, request, jsonify
import os
import hmac
import hashlib
import requests

app = Flask(__name__)

# Load sensitive info
API_KEY = os.getenv('c8a90d84e6c1098d453f216fdb0f6480d7b3cad202b68cc3')
API_SECRET = os.getenv('1b7888990f5090c993a4cc0ce89723462fa89982ff7dcc652adad5c6a064f62c')

HEADERS = {
    'Content-Type': 'application/json',
    'X-AUTH-APIKEY': API_KEY,
}

COINDCX_BASE = 'https://api.coindcx.com'

def place_order(side, symbol, quantity, leverage):
    path = "/exchange/v1/margin/create_order"
    body = {
        "symbol": symbol,
        "side": side.upper(),  # "buy" or "sell"
        "quantity": quantity,
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


@app.route('/', methods=['GET'])
def home():
    return "🚀 CoinDCX Margin Bot is Running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(f"[WEBHOOK RECEIVED] {data}")

    # Expecting TradingView to send: {"side": "buy", "symbol": "SUIUSDT", "qty": 10, "leverage": 3}
    try:
        side = data['side']
        symbol = data['symbol']
        qty = float(data['qty'])
        leverage = int(data.get('leverage', 2))  # default to 2x

        result = place_order(side, symbol, qty, leverage)
        return jsonify({"status": "success", "response": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

