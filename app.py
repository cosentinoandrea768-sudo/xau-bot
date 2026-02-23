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
        data = request.get_json(force=True)
        
        event = str(data.get("event",""))
        symbol = str(data.get("symbol",""))
        side = str(data.get("side",""))
        tf = str(data.get("timeframe","")) + "m" if "timeframe" in data else ""
        entry = data.get("entry")
        exit_price = data.get("exit")
        tp = data.get("tp")
        sl = data.get("sl")
        pips = data.get("profit_percent")

        lines = [f"{event} - {symbol} {side}"]
        if tf: lines.append(f"Timeframe: {tf}")
        if entry is not None and event=="OPEN": lines.append(f"Entry: {entry}")
        if tp is not None and event=="OPEN": lines.append(f"TP: {tp}")
        if sl is not None and event=="OPEN": lines.append(f"SL: {sl}")
        if exit_price is not None and event=="CLOSE": lines.append(f"Exit: {exit_price}")
        if pips is not None and event=="CLOSE":
            try: pips = round(float(pips),2)
            except: pass
            lines.append(f"Pips: {pips}")

        message = "\n".join(lines)
        payload = {"chat_id": CHAT_ID, "text": message}
        r = requests.post(TELEGRAM_URL, json=payload)
        print("Telegram response:", r.text)

        return jsonify({"status":"ok","telegram_response":r.text}),200

    except Exception as e:
        print("Errore webhook:", str(e))
        return jsonify({"error": str(e)}),500

@app.route("/", methods=["GET"])
def index():
    return "Telegram Bot attivo ✅",200

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
