from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    
    message = f"""
📈 ALERT STRATEGIA

Symbol: {data.get('ticker')}
Prezzo: {data.get('price')}
Side: {data.get('side')}
Timeframe: {data.get('timeframe')}
"""
    
    url = f"https://api.telegram.org/bot8393500223:AAHVRqD-22xUYLwMR1wgF0VUV_u4s6U9dR0/sendMessage"
    
    requests.post(url, json={
        "chat_id": 8369961034,
        "text": message
    })
    
    return "ok"

@app.route('/')
def home():
    return "Bot attivo"

if __name__ == "__main__":
    app.run()
