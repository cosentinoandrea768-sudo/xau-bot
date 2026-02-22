from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"


@app.route("/", methods=["GET"])
def home():
    return "Bot Telegram Webhook attivo", 200


@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)

        print("POST ricevuto:", data)

        message = data.get("message")

        if not message:
            return jsonify({"error": "No message field"}), 400

        payload = {
            "chat_id": CHAT_ID,
            "text": message
        }

        r = requests.post(TELEGRAM_URL, json=payload)

        print("Risposta Telegram:", r.text)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Errore:", str(e))
        return jsonify({"error": str(e)}), 500



