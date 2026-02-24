from flask import Flask, request, jsonify

app = Flask(__name__)

# Secret che deve coincidere con quello nel Pine Script
WEBHOOK_SECRET = "93ksk2kdk239dk"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)  # forza parsing JSON
        if not data:
            return "No JSON received", 400

        # Controlla il secret
        if "secret" not in data or data["secret"] != WEBHOOK_SECRET:
            return "Invalid secret", 400

        # Estrai i campi dal JSON
        event = data.get("event")
        symbol = data.get("symbol")
        timeframe = data.get("timeframe")
        side = data.get("side")
        entry = float(data.get("entry", 0))
        exit_price = float(data.get("exit", 0)) if data.get("exit") not in [None, "null"] else None
        tp = float(data.get("tp", 0))
        sl = float(data.get("sl", 0))
        profit_percent = float(data.get("profit_percent", 0)) if data.get("profit_percent") not in [None, "null"] else None

        # Qui puoi aggiungere la logica per il tuo bot Telegram o altri processi
        print(f"Webhook received: {event} {side} {symbol} entry={entry} tp={tp} sl={sl} profit={profit_percent}")

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        # Log dell'errore per debug
        print(f"Error in webhook: {e}")
        return "Internal Server Error", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
