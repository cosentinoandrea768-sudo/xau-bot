from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# ==========================
# VARIABILI AMBIENTE RENDER
# ==========================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not TELEGRAM_TOKEN or not CHAT_ID:
    print("ERRORE: TELEGRAM_TOKEN o CHAT_ID non impostati nelle variabili ambiente")

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"


# ==========================
# ROUTE WEBHOOK TRADINGVIEW
# ==========================
@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)

        if not data:
            return jsonify({"error": "No JSON received"}), 400

        message = data.get("message")

        if not message:
            return jsonify({"error": "No message field in JSON"}), 400

        payload = {
            "chat_id": CHAT_ID,
            "text": message
        }

        response = requests.post(TELEGRAM_URL, json=payload)

        if response.status_code == 200:
            print("Messaggio inviato a Telegram:", message)
            return jsonify({"status": "Message sent"}), 200
        else:
            print("Errore Telegram:", response.text)
            return jsonify({"error": "Telegram API error"}), 500

    except Exception as e:
        print("Errore webhook:", str(e))
        return jsonify({"error": str(e)}), 500


# ==========================
# ROUTE TEST (GET)
# ==========================
@app.route("/", methods=["GET"])
def home():
    return "Bot Telegram Webhook attivo", 200


# ==========================
# AVVIO SERVER
# ==========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
