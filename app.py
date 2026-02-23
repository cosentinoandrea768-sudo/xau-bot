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
        # Legge JSON
        data = request.get_json(silent=True)
        if not data:
            raw_data = request.data.decode("utf-8")
            try:
                data = json.loads(raw_data)
            except:
                data = {"event": raw_data}

        event = str(data.get("event", ""))
        symbol = str(data.get("symbol", ""))
        side = str(data.get("side", ""))

        # Entry, TP/SL, Exit, Profit
        entry = data.get("entry")
        tp = data.get("tp")
        sl = data.get("sl")
        exit_price = data.get("exit")
        profit_percent = data.get("profit_percent")

        # Timeframe in minuti
        tf_val = data.get("timeframe")
        tf_str = f"{tf_val}m" if tf_val is not None else ""

        # Costruisci messaggio solo con i campi esistenti
        message_lines = [f"{event} - {symbol} {side}"]
        if tf_str:
            message_lines.append(f"Timeframe: {tf_str}")
        if entry is not None:
            message_lines.append(f"Entry: {entry}")
        if tp is not None and event == "OPEN":
            message_lines.append(f"TP: {tp}")
        if sl is not None and event == "OPEN":
            message_lines.append(f"SL: {sl}")
        if exit_price is not None and event == "CLOSE":
            message_lines.append(f"Exit: {exit_price}")
        if profit_percent is not None and event == "CLOSE":
            try:
                profit_percent = round(float(profit_percent), 2)
            except:
                pass
            message_lines.append(f"Profit %: {profit_percent}")

        message = "\n".join(message_lines)

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
