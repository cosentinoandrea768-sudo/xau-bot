@app.route("/", methods=["POST"])
def webhook():
    try:
        # Proviamo a leggere JSON
        data = request.get_json(silent=True)

        # Se non è JSON, leggiamo il testo puro
        if not data:
            raw_data = request.data.decode("utf-8")
            print("Raw body:", raw_data)
            message = raw_data
        else:
            print("JSON ricevuto:", data)
            message = data.get("message", str(data))

        if not message:
            return jsonify({"error": "No message received"}), 400

        payload = {
            "chat_id": CHAT_ID,
            "text": message
        }

        r = requests.post(TELEGRAM_URL, json=payload)
        print("Risposta Telegram:", r.text)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Errore:", str(e))
        return jsonify({"error": str(e)}), 500
