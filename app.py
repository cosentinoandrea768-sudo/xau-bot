from flask import Flask, request, jsonify
import requests
import os
import json

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# =============================
# HEALTH CHECK
# =============================
@app.route("/", methods=["GET", "HEAD"])
def home():
    return "OK", 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running"}), 200


# =============================
# FORMAT MESSAGE
# =============================
def format_message(data):

    event = data.get("event", "")
    symbol = data.get("symbol", "")
    timeframe = data.get("timeframe", "")
    side = data.get("side", "")
    entry = data.get("entry", "")
    exit_price = data.get("exit", "")
    tp = data.get("tp", "")
    sl = data.get("sl", "")
    profit_percent = data.get("profit_percent", "")

    # arrotondamenti a 3 decimali
    def round3(value):
        try:
            return f"{float(value):.3f}"
        except:
            return value

    entry = round3(entry)
    tp = round3(tp)
    sl = round3(sl)

    if event == "OPEN":

        emoji = "🚀" if side == "LONG" else "⬇️"

        return (
            f"{emoji} {side}\n"
            f"Pair: {symbol}\n"
            f"Timeframe: {timeframe}m\n"
            f"Price: {entry}\n"
            f"TP: {tp}\n"
            f"SL: {sl}"
        )

    elif event == "CLOSE":

        try:
            profit = float(profit_percent)
            sign = "+" if profit >= 0 else "-"
            profit_str = f"{sign}{abs(profit):.2f}%"
        except:
            profit_str = "0.00%"

        return (
            f"⚡ EXIT {side}\n"
            f"Pair: {symbol}\n"
            f"Result: {profit_str}"
        )

    return "Messaggio non riconosciuto"


# =============================
# WEBHOOK
# =============================
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        raw_data = request.get_data(as_text=True)

        if not raw_data:
            return jsonify({"error": "Empty body"}), 400

        data = json.loads(raw_data)

        message = format_message(data)

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
