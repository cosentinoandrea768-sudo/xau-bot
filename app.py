from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# ==============================
# Variabili Telegram (Render Environment)
# ==============================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# ==============================
# Funzione invio Telegram
# ==============================
def send_telegram(message):
    try:
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        r = requests.post(TELEGRAM_URL, json=payload, timeout=5)
        print("Telegram response:", r.text)
    except Exception as e:
        print("Errore invio Telegram:", str(e))

# ==============================
# Webhook TradingView
# ==============================
@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "No JSON received"}), 400

        # 🔐 Controllo secret
        if data.get("secret") != WEBHOOK_SECRET:
            return jsonify({"error": "Unauthorized"}), 403

        # Legge dati dal webhook
        event = data.get("event")
        symbol = data.get("symbol")
        timeframe = data.get("timeframe")
        side = data.get("side")
        entry = data.get("entry", "NaN")
        exit_price = data.get("exit", "NaN")
        tp = data.get("tp", "NaN")
        sl = data.get("sl", "NaN")
        profit = data.get("profit_percent", "NaN")

        # Costruzione messaggio leggibile
        tf_str = f"{timeframe}m"
        if event == "OPEN":
            message = f"<b>🟢 {side} OPEN</b>\n" \
                      f"Symbol: {symbol}\n" \
                      f"Timeframe: {tf_str}\n" \
                      f"Entry: {entry}\n" \
                      f"TP: {tp}\n" \
                      f"SL: {sl}"
        elif event == "TP_HIT":
            message = f"<b>🎯 TAKE PROFIT HIT</b>\n" \
                      f"Symbol: {symbol}\n" \
                      f"Side: {side}\n" \
                      f"Exit: {exit_price}\n" \
                      f"Profit: {profit} %"
        elif event == "SL_HIT":
            message = f"<b>❌ STOP LOSS HIT</b>\n" \
                      f"Symbol: {symbol}\n" \
                      f"Side: {side}\n" \
                      f"Exit: {exit_price}\n" \
                      f"Loss: {profit} %"
        else:
            message = f"⚠️ Unknown event: {event}\n{data}"

        send_telegram(message)
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Errore:", str(e))
        return jsonify({"error": str(e)}), 500

# ==============================
# Health check per Uptime Robot
# ==============================
@app.route("/", methods=["GET"])
def index():
    return "TradingView → Telegram Bot PRO attivo 🚀", 200
