from flask import Flask, request, jsonify
import requests
import os
import json

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

app = Flask(__name__)

@app.route("/", methods=["POST"])
def webhook():
    try:
        # Prova a leggere JSON
        data = request.get_json(silent=True)

        # Se non è JSON, prova a leggere testo e parsarlo
        if not data:
            raw_data = request.data.decode("utf-8")
            try:
                data = json.loads(raw_data)
            except:
                # Se non è JSON, metti il testo intero in "message"
                data = {"event": raw_data}

        # Assicuriamoci di avere sempre le chiavi
        event = str(data.get("event", "N/A"))
        symbol = str(data.get("symbol", "N/A"))
        side = str(data.get("side", "N/A"))
        entry = str(data.get("entry", "N/A"))
        exit_price = str(data.get("exit", "N/A"))
        tp = str(data.get("tp", "N/A"))
        sl = str(data.get("sl", "N/A"))
        profit_percent = str(data.get("profit_percent", "N/A"))

        message = f"{event} - {symbol} {side}\nEntry: {entry}\nExit: {exit_price}\nTP: {tp}\nSL: {sl}\nProfit %: {profit_percent}"

        payload = {"chat_id": CHAT_ID, "text": message}

        r = requests.post(TELEGRAM_URL, json=payload)
        print("Telegram response:", r.text)

        return jsonify({"status": "ok", "telegram_response": r.text}), 200

    except Exception as e:
        print("Errore webhook:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def index():
    return "Telegram Bot Webhook attivo ✅", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
