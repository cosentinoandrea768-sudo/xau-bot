# app.py
from flask import Flask, request, jsonify
import requests
import os

# ==============================
# Variabili Telegram (da impostare su Render)
# ==============================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# ==============================
# Creazione app Flask
# ==============================
app = Flask(__name__)

# ==============================
# Webhook per TradingView
# ==============================
@app.route("/", methods=["POST"])
def webhook():
    try:
        # Prova a leggere JSON
        data = request.get_json(silent=True)

        # Se non è JSON, leggiamo il testo puro
        if not data:
            raw_data = request.data.decode("utf-8")
            print("Raw body:", raw_data)
            message = raw_data
        else:
            print("JSON ricevuto:", data)
            message = data.get("message", str(data))

        if not message:
            return jsonify({"error": "No message received"}), 400

        # Payload per Telegram
        payload = {
            "chat_id": CHAT_ID,
            "text": message
        }

        # Invia messaggio a Telegram
        r = requests.post(TELEGRAM_URL, json=payload)
        print("Risposta Telegram:", r.text)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Errore:", str(e))
        return jsonify({"error": str(e)}), 500

# ==============================
# Endpoint base per test
# ==============================
@app.route("/", methods=["GET"])
def index():
    return "Bot Telegram Webhook attivo ✅", 200
