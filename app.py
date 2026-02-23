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
# Funzione per formattare il messaggio Telegram
# ==============================
def format_message(data: dict) -> str:
    event = data.get("event", "")
    side = data.get("side", "")
    symbol = data.get("symbol", "")
    timeframe = data.get("timeframe", "")
    entry = data.get("entry", "")
    exit_price = data.get("exit", "")
    tp = data.get("tp", "")
    sl = data.get("sl", "")
    profit_percent = data.get("profit_percent", "")

    # Formatta con massimo 2 decimali per pips/profit/loss
    try:
        if profit_percent != "NaN":
            profit_percent = f"{float(profit_percent):.2f}"
    except:
        pass

    if event == "OPEN":
        msg = f"💹 {side} ENTRY\nPair: {symbol}\nTimeframe: {timeframe}m\nPrice: {entry}\nTP: {tp}\nSL: {sl}"
    else:
        # Chiudi trade
        pips_sign = "+" if float(profit_percent) >= 0 else "-"
        msg = f"⚡ {side} EXIT\nPair: {symbol}\nResult: {pips_sign}{abs(float(profit_percent))}%"
    return msg

# ==============================
# Webhook endpoint
# ==============================
@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "No JSON received"}), 400

        message = format_message(data)

        payload = {
            "chat_id": CHAT_ID,
            "text": message
        }

        r = requests.post(TELEGRAM_URL, json=payload)

        if r.status_code != 200:
            return jsonify({"error": f"Telegram API error: {r.text}"}), 500

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Errore webhook:", str(e))
        return jsonify({"error": str(e)}), 500

# ==============================
# Endpoint base per test
# ==============================
@app.route("/", methods=["GET"])
def index():
    return "Bot Telegram Webhook attivo ✅", 200

# ==============================
# Main (per test locale)
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
