from flask import Flask, request, jsonify
import requests
import os
import json

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

app = Flask(__name__)

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

    try:
        if profit_percent not in ["NaN", None, ""]:
            profit_percent = f"{float(profit_percent):.2f}"
    except:
        profit_percent = "NaN"

    if event == "OPEN":
        emoji = "🚀" if side == "LONG" else "⬇️"
        msg = f"{emoji} {side} ENTRY\nPair: {symbol}\nTimeframe: {timeframe}m\nPrice: {entry}\nTP: {tp}\nSL: {sl}"
    else:
        try:
            pips_val = float(profit_percent)
            pips_sign = "+" if pips_val >= 0 else "-"
            msg = f"⚡ {side} EXIT\nPair: {symbol}\nResult: {pips_sign}{abs(pips_val)}%"
        except:
            msg = f"⚡ {side} EXIT\nPair: {symbol}\nResult: {profit_percent}%"
    return msg

@app.route("/", methods=["POST"])
def webhook():
    try:
        # prima prova a leggere JSON standard
        data = request.get_json(silent=True)

        # se fallisce, prova come stringa e fai il parse
        if not data:
            raw_data = request.data.decode("utf-8")
            try:
                data = json.loads(raw_data)
            except Exception as e:
                return jsonify({"error": "Invalid JSON payload", "details": str(e)}), 400

        message = format_message(data)

        payload = {"chat_id": CHAT_ID, "text": message}

        r = requests.post(TELEGRAM_URL, json=payload)
        if r.status_code != 200:
            return jsonify({"error": f"Telegram API error: {r.text}"}), 500

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Errore webhook:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def index():
    return "Bot Telegram Webhook attivo ✅", 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Flask app on port {port}")
    app.run(host="0.0.0.0", port=port)
