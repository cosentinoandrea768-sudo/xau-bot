from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# ==============================
# Variabili Telegram (da impostare su Render)
# ==============================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# ==============================
# Funzione invio Telegram
# ==============================
def send_telegram(message):
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    r = requests.post(TELEGRAM_URL, json=payload)
    print("Telegram:", r.text)

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

        event = data.get("event")
        symbol = data.get("symbol")
        timeframe = data.get("timeframe")
        side = data.get("side")

        entry = float(data.get("entry", 0))
        exit_price = float(data.get("exit", 0))
        tp = float(data.get("tp", 0))
        sl = float(data.get("sl", 0))
        profit = float(data.get("profit_percent", 0))

        # ==========================
        # Calcolo R:R reale
        # ==========================
        rr_real = 0
        if event in ["TP_HIT", "SL_HIT"] and entry != 0:
            risk = abs(entry - sl)
            reward = abs(exit_price - entry)
            if risk != 0:
                rr_real = round(reward / risk, 2)

        # ==========================
        # Formattazione messaggi Telegram
        # ==========================
        if event == "OPEN":
            message = f"<b>🟢 {side} OPEN</b>\n" \
                      f"Symbol: {symbol}\n" \
                      f"Timeframe: {timeframe}m\n" \
                      f"Entry: {entry}\n" \
                      f"TP: {tp}\n" \
                      f"SL: {sl}"

        elif event == "TP_HIT":
            message = f"<b>🎯 TAKE PROFIT HIT</b>\n" \
                      f"Symbol: {symbol}\n" \
                      f"Side: {side}\n" \
                      f"Exit: {exit_price}\n" \
                      f"Profit: {profit:.2f} %\n" \
                      f"R:R: {rr_real}"

        elif event == "SL_HIT":
            message = f"<b>❌ STOP LOSS HIT</b>\n" \
                      f"Symbol: {symbol}\n" \
                      f"Side: {side}\n" \
                      f"Exit: {exit_price}\n" \
                      f"Loss: {profit:.2f} %\n" \
                      f"R:R: {rr_real}"

        else:
            message = f"⚠️ Unknown event: {event}\n{data}"

        send_telegram(message)
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Errore:", str(e))
        return jsonify({"error": str(e)}), 500

# ==============================
# Endpoint GET di test
# ==============================
@app.route("/", methods=["GET"])
def index():
    return "TradingView → Telegram Bot PRO attivo 🚀", 200
