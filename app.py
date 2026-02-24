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
# Stato segnali trend
# -----------------------
last_trend_signal = {}  # es: {'BTCUSDT': {'type':'MIN', 'value':25000, 'ts': 167676}}

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
# Funzione calcolo profit sul singolo trade
# -----------------------
def format_profit(entry, exit_price, side):
    try:
        entry_f = float(entry)
        exit_f = float(exit_price)
        if side.upper() == "LONG":
            profit = (exit_f - entry_f) / entry_f * 100
        else:  # SHORT
            profit = (entry_f - exit_f) / entry_f * 100
        return f"{profit:.2f}%"
    except:
        return "-"

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

        # Arrotondamenti
        try:
            entry = f"{float(entry):.3f}"
        except: pass
        try:
            tp = f"{float(tp):.3f}"
        except: pass
        try:
            sl = f"{float(sl):.3f}"
        except: pass
        try:
            exit_price = f"{float(exit_price):.3f}"
        except: pass

        # Apertura trade
        if event in ["OPEN", "REVERSAL_OPEN"]:
            emoji = "🚀" if side.upper() == "LONG" else "🔻"
            if event == "REVERSAL_OPEN":
                emoji = "🔄"
            message = (
                f"{emoji} {side.upper()}\n"
                f"Pair: {symbol}\n"
                f"Timeframe: {timeframe}\n"
                f"Price: {entry}\n"
                f"TP: {tp}\n"
                f"SL: {sl}"
            )
            return message

        # Chiusura trade
        elif event in ["TP_HIT", "SL_HIT", "CLOSE"]:
            # Determina TP o SL in caso di CLOSE
            if event == "CLOSE":
                try:
                    entry_f = float(entry)
                    exit_f = float(exit_price)
                    tp_f = float(tp)
                    sl_f = float(sl)
                    if side.upper() == "LONG":
                        if exit_f >= tp_f:
                            label = "TP HIT"
                        elif exit_f <= sl_f:
                            label = "SL HIT"
                        else:
                            label = "CLOSE"
                    else:  # SHORT
                        if exit_f <= tp_f:
                            label = "TP HIT"
                        elif exit_f >= sl_f:
                            label = "SL HIT"
                        else:
                            label = "CLOSE"
                except:
                    label = "CLOSE"
            else:
                label = "TP HIT" if event == "TP_HIT" else "SL HIT"

            profit = format_profit(entry, exit_price, side)
            message = (
                f"⚡ {label} {side.upper()}\n"
                f"Pair: {symbol}\n"
                f"Timeframe: {timeframe}\n"
                f"Entry: {entry}\n"
                f"Exit: {exit_price}\n"
                f"Profit: {profit}"
            )
            return message

        else:
            return f"{symbol}: {event}"
    else:
        return str(data)

# -----------------------
# Webhook POST per trade (strategia)
# -----------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        raw_data = request.data
        print("Raw body ricevuto:", raw_data)

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

        # Logica reversal basata sui segnali trend
        if isinstance(data, dict):
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
        print(f"Error in webhook: {e}")
        return "Internal Server Error", 500

# -----------------------
# Webhook POST per segnali trend (forza trend)
# -----------------------
@app.route("/webhook/trend", methods=["POST"])
def trend_webhook():
    try:
        data = request.json
        symbol = data.get("symbol")
        event_type = data.get("event")  # MIN o MAX
        value = data.get("value")

        last_trend_signal[symbol] = {
            "type": event_type,
            "value": value,
            "ts": time.time()
        }

        print(f"Segnale trend ricevuto: {symbol} {event_type} a {value}")
        return jsonify({"status":"ok"}), 200
    except Exception as e:
        print(f"Error in trend_webhook: {e}")
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
