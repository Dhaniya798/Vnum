import json
import requests
from http.server import BaseHTTPRequestHandler

TOKEN = "8355016420:AAFnAheJgoKgvQiOQ0J6dGMoIHowVC3mpcU"
API_BASE = "https://encorexapi.vercel.app/vehicletest?vnum="

WEBHOOK_PATH = f"/{TOKEN}"

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != WEBHOOK_PATH:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
            return

        try:
            content_length = int(self.headers.get('content-length', '0'))
            if content_length == 0:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK - No body")
                return

            post_data = self.rfile.read(content_length).decode('utf-8', errors='ignore')
            update = json.loads(post_data)

            reply = "Bot received message. Processing..."

            if 'message' in update:
                chat_id = update['message'].get('chat', {}).get('id')
                text = update['message'].get('text', '').strip().upper()

                if not chat_id:
                    reply = "No chat ID found."
                elif text == '/start':
                    reply = "Vehicle lookup bot ready. Send vehicle number like RJ07CC8989"
                elif len(text) >= 8 and text.isalnum():
                    try:
                        url = API_BASE + text
                        resp = requests.get(url, timeout=10)
                        resp.raise_for_status()
                        data = resp.json()
                        d = data.get("data", {}).get("data", {}).get("data", [{}])[0] or {}

                        reply = f"Details for {text}:\n\n"
                        reply += f"Owner: {d.get('owner_name', 'N/A')}\n"
                        reply += f"Father: {d.get('father_name', 'N/A')}\n"
                        reply += f"Mobile: {d.get('mobile_no', 'N/A')}\n"
                        reply += f"Model: {d.get('vehicle_model', 'N/A')}\n"
                        reply += f"Fuel: {d.get('fuel_type', 'N/A')}\n"
                        reply += f"Reg Date: {d.get('regn_dt', 'N/A')}\n"
                        reply += f"Insurance Until: {d.get('ins_upto', 'N/A')}\n"
                    except Exception as api_err:
                        reply = f"API error: {str(api_err)}. Check number or API status."
                else:
                    reply = "Send valid vehicle number (alphanumeric, min 8 chars)."

                # Send reply safely
                try:
                    send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                    requests.post(send_url, json={"chat_id": chat_id, "text": reply}, timeout=10)
                except:
                    pass  # Silent fail for now

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception as e:
            self.send_response(200)  # Telegram ko 200 hi dena padta hai warna retry
            self.end_headers()
            self.wfile.write(b"OK")  # Always 200 to avoid Telegram retry loop
            # Log error for Vercel (print shows in logs)
            print(f"CRASH: {str(e)} - Path: {self.path} - Headers: {self.headers}")

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Webhook active. POST for Telegram updates.")
