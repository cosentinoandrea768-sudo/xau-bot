from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# -----------------------
# Variabili d'ambiente
# -----------------------
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("CHAT_ID")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID or not WEBHOOK_SECRET:
    raise ValueError("Assicurati di avere impostato TELEGRAM_TOKEN, CHAT_ID e WEBHOOK_SECRET su Render!")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# -----------------------
# Funzione invio Telegram
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
# Formatta messaggio trade
# -----------------------
def format_message(data):
    if isinstance(data, dict):
        event = data.get("event", "")
        symbol = data.get("symbol", "")
        timeframe = data.get("timeframe", "")
        side = data.get("side", "")
        entry = data.get("entry", "N/A")
        exit_price = data.get("exit", "N/A")
        tp = data.get("tp", "N/A")
        sl = data.get("sl", "N/A")
        profit = data.get("profit_percent", "-")

        # Arrotondamenti
        try:
            entry = f"{float(entry):.2f}"
        except: pass
        try:
            exit_price = f"{float(exit_price):.2f}"
        except: pass
        try:
            tp = f"{float(tp):.2f}"
        except: pass
        try:
            sl = f"{float(sl):.2f}"
        except: pass
        try:
            profit_f = float(profit)
            if side.upper() == "SHORT":
                profit_f = abs(profit_f)
            profit = f"{profit_f:.2f}%"
        except: pass

        # Messaggio apertura trade
        if event == "OPEN":
            emoji = "🚀" if side.upper() == "LONG" else "🔻"
            message = f"{emoji} {symbol} {timeframe}m\nEntry: {entry}\nTP: {tp}\nSL: {sl}"
            return message

        # Messaggio chiusura trade
        elif "TP" in event or "SL" in event:
            exit_type = "Exit Long" if side.upper() == "LONG" else "Exit Short"
            message = f"{exit_type} {symbol}\nPips: TP {tp}, SL {sl}\nProfit: {profit}"
            return message

        else:
            return f"{symbol}: {event}"  # fallback minimo

    else:
        # Testo semplice, invia grezzo senza "messaggio ricevuto"
        return str(data)

# -----------------------
# Webhook POST
# -----------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        raw_data = request.data
        print("Raw body ricevuto:", raw_data)

        # Proviamo a parsare JSON
        try:
            data = json.loads(raw_data)
            is_json = True
        except Exception:
            data = raw_data.decode("utf-8")
            is_json = False
            print("Non è JSON, invio testo grezzo:", data)

        # Controllo secret solo se JSON
        if is_json:
            if "secret" not in data or data["secret"] != WEBHOOK_SECRET:
                return "Invalid secret", 400

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
    print("Ping UptimeRobot ricevuto su /")
    return "Bot online ✅", 200

# -----------------------
# Avvio app
# -----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
