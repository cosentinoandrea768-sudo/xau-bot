from flask import Flask, request, jsonify
import requests
import os

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

app = Flask(__name__)

@app.route("/", methods=["POST"])
def webhook():
    try:
        # Leggi il body raw (TradingView spesso manda text/plain)
        raw_data = request.data.decode("utf-8")
        print("Raw body:", raw_data)

        # Invia a Telegram
        payload = {
            "chat_id": CHAT_ID,
            "text": raw_data
        }
        r = requests.post(TELEGRAM_URL, json=payload)
        print("Telegram response:", r.text)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Errore:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def index():
    return "Bot Telegram Webhook attivo ✅", 200
