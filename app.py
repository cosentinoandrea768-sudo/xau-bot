from flask import Flask, request, jsonify
import requests
import os

# ==============================
# Variabili Telegram (impostare su Render)
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
        # Legge JSON dal webhook
        data = request.get_json(force=True)

        if not data:
            return jsonify({"error": "No data received"}), 400

        # Crea il messaggio Telegram
        message = f"{data.get('event','')} - {data.get('symbol','')} {data.get('side','')}\n" \
                  f"Entry: {data.get('entry','')}\nExit: {data.get('exit','')}\n" \
                  f"TP: {data.get('tp','')}\nSL: {data.get('sl','')}\nProfit %: {data.get('profit_percent','')}"

        payload = {"chat_id": CHAT_ID, "text": message}

        # Invio messaggio Telegram
        r = requests.post(TELEGRAM_URL, json=payload)

        return jsonify({"status": "ok", "telegram_response": r.text}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==============================
# Endpoint GET per test
# ==============================
@app.route("/", methods=["GET"])
def index():
    return "Telegram Bot Webhook attivo ✅", 200

# ==============================
# Avvio app
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
