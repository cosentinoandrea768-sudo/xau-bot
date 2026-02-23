from flask import Flask, request, jsonify
import requests
import os
import json

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

@app.route("/", methods=["GET"])
def index():
    return "Bot Telegram Webhook attivo ✅", 200

@app.route("/", methods=["POST"])
def webhook():
    try:
        # Prendiamo SEMPRE il body grezzo
        raw_data = request.get_data(as_text=True)

        if not raw_data:
            return jsonify({"error": "Empty body"}), 400

        # Proviamo a convertirlo in JSON
        try:
            data = json.loads(raw_data)
        except:
            # Se non è JSON valido, lo mandiamo comunque come testo
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
