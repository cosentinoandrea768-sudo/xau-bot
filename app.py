from flask import Flask, request, jsonify
import requests
import json
import os
import html
import time

# -----------------------
# Flask app WSGI compatibile
# -----------------------
application = Flask(__name__)

# -----------------------
# Variabili d'ambiente
# -----------------------
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("CHAT_ID")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID or not WEBHOOK_SECRET:
    raise ValueError("Assicurati di avere impostato TELEGRAM_TOKEN, CHAT_ID e WEBHOOK_SECRET!")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# -----------------------
# Stato segnali trend
# -----------------------
last_trend_signal = {}

# -----------------------
# Funzione invio Telegram
# -----------------------
def send_telegram_message(text):
    try:
        safe_text = html.escape(text)
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": safe_text,
            "parse_mode": "HTML"
        }
        r = requests.post(TELEGRAM_API_URL, json=payload, timeout=10)
        r.raise_for_status()
        print("Messaggio inviato:", r.json())
    except Exception as e:
        print(f"Errore invio Telegram: {e}")

# -----------------------
# Formatta messaggio trade
# -----------------------
def format_message(data):

    if not isinstance(data, dict):
        return str(data)

    event = data.get("event", "")
    symbol = data.get("symbol", "")
    timeframe = data.get("timeframe", "")
    side = data.get("side", "").upper()
    entry = data.get("entry")
    exit_price = data.get("exit")
    tp = data.get("tp")
    sl = data.get("sl")

    # Conversioni numeriche sicure
    try: entry = float(entry)
    except: entry = None
    try: exit_price = float(exit_price)
    except: exit_price = None
    try: tp = float(tp)
    except: tp = None
    try: sl = float(sl)
    except: sl = None

    # ---------------- CALCOLO PIPS ----------------
    pips_value = None

    if entry is not None and exit_price is not None:

        if side == "LONG":
            pips_value = exit_price - entry
        elif side == "SHORT":
            pips_value = entry - exit_price
        else:
            pips_value = exit_price - entry

        pips_value = round(pips_value, 2)

    # Formattazione con + solo su TP
    if pips_value is not None:
        if event == "TP_HIT":
            pips_text = f"+{abs(pips_value):.2f} pips"
        elif event == "SL_HIT":
            pips_text = f"-{abs(pips_value):.2f} pips"
        else:
            pips_text = f"{pips_value:.2f} pips"
    else:
        pips_text = "N/A"

    # ---------------- EMOJI ----------------
    emoji_open = "🚀" if side == "LONG" else "🔻"
    emoji_tp = "🟢"
    emoji_sl = "🔴"
    emoji_close = "⚡️"
    emoji_reversal = "🔄"

    # ---------------- APERTURA ----------------
    if event in ["OPEN", "REVERSAL_OPEN"]:

        if event == "REVERSAL_OPEN":
            header = f"{emoji_reversal} REVERSAL {side}"
        else:
            header = f"{emoji_open} {side}"

        return (
            f"{header}\n"
            f"Pair: {symbol}\n"
            f"Timeframe: {timeframe}\n"
            f"Entry: {entry}\n"
            f"TP: {tp}\n"
            f"SL: {sl}"
        )

    # ---------------- CHIUSURA ----------------
    elif event in ["TP_HIT", "SL_HIT", "CLOSE"]:

        if event == "TP_HIT":
            header = f"{emoji_tp} TP HIT"
        elif event == "SL_HIT":
            header = f"{emoji_sl} SL HIT"
        else:
            header = f"{emoji_close} CLOSE"

        return (
            f"{header}\n"
            f"{side}\n"
            f"Pair: {symbol}\n"
            f"Timeframe: {timeframe}\n"
            f"Entry: {entry}\n"
            f"Exit: {exit_price}\n"
            f"Profit: {pips_text}"
        )

    # ---------------- ALTRO ----------------
    return f"{symbol}: {event}"

# -----------------------
# Webhook principale
# -----------------------
@application.route("/webhook", methods=["POST"])
def webhook():
    try:
        raw_data = request.data
        data = json.loads(raw_data)

        if "secret" not in data or data["secret"] != WEBHOOK_SECRET:
            return "Invalid secret", 400

        # Logica reversal
        symbol = data.get("symbol")
        trend = last_trend_signal.get(symbol)

        if trend:
            side = data.get("side", "").upper()
            if trend["type"] == "MIN" and side == "LONG":
                data["event"] = "REVERSAL_OPEN"
            elif trend["type"] == "MAX" and side == "SHORT":
                data["event"] = "REVERSAL_OPEN"

        message = format_message(data)
        send_telegram_message(message)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Errore webhook:", e)
        return "Internal Server Error", 500

# -----------------------
# Webhook trend
# -----------------------
@application.route("/webhook/trend", methods=["POST"])
def trend_webhook():
    try:
        data = request.json
        symbol = data.get("symbol")
        event_type = data.get("event")
        value = data.get("value")

        last_trend_signal[symbol] = {
            "type": event_type,
            "value": value,
            "ts": time.time()
        }

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Errore trend webhook:", e)
        return "Internal Server Error", 500

# -----------------------
# Endpoint uptime
# -----------------------
@application.route("/", methods=["GET"])
def uptime():
    return "Bot online ✅", 200

# -----------------------
# Avvio
# -----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    application.run(host="0.0.0.0", port=port)
