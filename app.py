from flask import Flask, request, jsonify
import requests
import json
import os
import html
import time

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
    try:
        safe_text = html.escape(text)
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": safe_text,
            "parse_mode": "HTML"
        }
        print("Invio payload Telegram:", payload)
        r = requests.post(TELEGRAM_API_URL, json=payload, timeout=10)
        r.raise_for_status()
        print("Messaggio inviato correttamente:", r.json())
    except requests.exceptions.HTTPError as e:
        print(f"Errore invio Telegram HTTP: {e.response.text}")
    except Exception as e:
        print(f"Errore invio Telegram generico: {e}")

# -----------------------
# Formatta messaggio indicatore di forza
# -----------------------
def format_exhaustion_message(data):
    pair = data.get("pair", "")
    score = data.get("score", "")
    zone = data.get("zone", "")
    link = data.get("link", "")
    timeframe = data.get("timeframe", "")  # 🔹 Nuovo campo

    text = f"Pair: {pair}\nScore: {score}\nZona: {zone}\nTimeframe: {timeframe}\n"
    if zone == 70:
        text += "Possibile massimo locale\n"
    elif zone == 30:
        text += "Possibile minimo locale\n"
    text += link
    return text

# -----------------------
# Webhook POST per segnali forza trend / indicatore
# -----------------------
@app.route("/webhook/exhaustion", methods=["POST"])
def exhaustion_webhook():
    try:
        data = request.json
        message = format_exhaustion_message(data)
        send_telegram_message(message)
        print(f"Segnale exhaustion ricevuto: {data.get('pair')} zona {data.get('zone')} score {data.get('score')}")
        return jsonify({"status":"ok"}), 200
    except Exception as e:
        print(f"Error in exhaustion_webhook: {e}")
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
