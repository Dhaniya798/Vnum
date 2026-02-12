import telebot
from flask import Flask, request
import requests
import os

# Replace with your Bot Token
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

bot = telebot.TeleBot(8355016420:AAFnAheJgoKgvQiOQ0J6dGMoIHowVC3mpcU)
app = Flask(__name__)

API_BASE = "https://encorexapi.vercel.app/vehicletest?vnum="

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Vehicle details lookup bot. Send me a vehicle number like RJ07CC8989.")

@bot.message_handler(func=lambda message: True)
def handle_vehicle_number(message):
    vnum = message.text.strip().upper()
    try:
        url = API_BASE + vnum
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()["data"]["data"]["data"][0]
        
        reply = f"Vehicle Details for {vnum}:\n\n"
        reply += f"Owner Name: {data.get('owner_name', 'N/A')}\n"
        reply += f"Father Name: {data.get('father_name', 'N/A')}\n"
        reply += f"Mobile: {data.get('mobile_no', 'N/A')}\n"
        reply += f"RTO: {data.get('rto', 'N/A')}\n"
        reply += f"Manufacturer: {data.get('maker', 'N/A')}\n"
        reply += f"Model: {data.get('vehicle_model', 'N/A')}\n"
        reply += f"Fuel Type: {data.get('fuel_type', 'N/A')}\n"
        reply += f"Reg Date: {data.get('regn_dt', 'N/A')}\n"
        reply += f"Insurance Until: {data.get('ins_upto', 'N/A')}\n"
        reply += f"PUC Until: {data.get('puc_upto', 'N/A')}\n"
        reply += f"Blacklist: {data.get('blacklist_status', 'N/A')}\n"
        
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}. Check number or try later.")

@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"https://your-vercel-app-name.vercel.app/{BOT_TOKEN}")
    return "Webhook set!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
