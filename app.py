from flask import Flask, request, jsonify
import requests
import os
import json

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# =============================
# HEALTH CHECK (UptimeRobot)
# =============================
@app.route("/", methods=["GET", "HEAD"])
def home():
    return "OK", 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running"}), 200

# =============================
# WEBHOOK (TradingView)
# =============================
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        raw_data = request.get_data(as_text=True)

        if not raw_data:
            return jsonify({"error": "Empty body"}), 400

        try:
            data = json.loads(raw_data)
        except:
            data = {"raw": raw_data}

        message = f"Webhook ricevuto:\n{data}"

        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

        payload = {
            "chat_id": CHAT_ID,
            "text": message
        }

        r = requests.post(telegram_url, json=payload)

        if r.status_code != 200:
            return jsonify({"telegram_error": r.text}), 500

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
