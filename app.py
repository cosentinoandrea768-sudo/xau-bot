from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# -----------------------
# Configura bot Telegram
# -----------------------
TELEGRAM_TOKEN = "IL_TUO_BOT_TOKEN"
TELEGRAM_CHAT_ID = "IL_TUO_CHAT_ID"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# -----------------------
# Secret per il webhook
# -----------------------
WEBHOOK_SECRET = "93ksk2kdk239dk"

# -----------------------
# Funzione per inviare messaggio Telegram
# -----------------------
def send_telegram_message(text):
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(TELEGRAM_API_URL, json=payload, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"Errore invio Telegram: {e}")

# -----------------------
# Funzione per formattare JSON in messaggio leggibile
# -----------------------
def format_message(data):
    event = data.get("event", "")
    symbol = data.get("symbol", "")
    timeframe = data.get("timeframe", "")
    side = data.get("side", "")
    entry = data.get("entry", "N/A")
    exit_price = data.get("exit", "N/A")
    tp = data.get("tp", "N/A")
    sl = data.get("sl", "N/A")
    profit = data.get("profit_percent", "-")
    
    if profit in [None, "null"]:
        profit = "-"
    if exit_price in [None, "null"]:
        exit_price = "-"
    
    emoji = "✅" if event == "OPEN" else ("🎯" if "TP" in event else "🛑")
    
    message = f"{emoji} {event}\nSymbol: {symbol}\nTimeframe: {timeframe}\nSide: {side}\nEntry: {entry}\nExit: {exit_price}\nTP: {tp}\nSL: {sl}\nProfit %: {profit}"
    return message

# -----------------------
# Endpoint webhook POST
# -----------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # Legge raw body per debug
        raw_data = request.data
        print("Raw body ricevuto:", raw_data)

        # Prova a parsare il JSON
        try:
            data = json.loads(raw_data)
        except Exception as e:
            print(f"Errore parsing JSON: {e}")
            return "Invalid JSON", 400

        print("JSON parsato:", data)

        # Controllo secret
        if "secret" not in data or data["secret"] != WEBHOOK_SECRET:
            return "Invalid secret", 400

        # Formatta e invia messaggio su Telegram
        message = format_message(data)
        send_telegram_message(message)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print(f"Error in webhook: {e}")
        return "Internal Server Error", 500

# -----------------------
# Endpoint GET per UptimeRobot
# -----------------------
@app.route("/", methods=["GET"])
def uptime():
    print("Ping UptimeRobot ricevuto")
    return "Bot online ✅", 200

# -----------------------
# Avvio app
# -----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
