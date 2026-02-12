import json
import os
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
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Bad Request: No body")
                return

            post_data = self.rfile.read(content_length).decode('utf-8')
            update = json.loads(post_data)

            if 'message' in update:
                chat_id = update['message']['chat']['id']
                text = update['message'].get('text', '').strip().upper()

                if text == '/start':
                    reply = "Vehicle lookup bot ready. Send vehicle number like RJ07CC8989"
                elif len(text) >= 8 and text.isalnum():
                    try:
                        url = API_BASE + text
                        resp = requests.get(url, timeout=10)
                        resp.raise_for_status()  # Raise if not 200
                        data = resp.json()
                        d = data["data"]["data"]["data"][0]

                        reply = f"Details for {text}:\n\n"
                        reply += f"Owner: {d.get('owner_name', 'N/A')}\n"
                        reply += f"Father: {d.get('father_name', 'N/A')}\n"
                        reply += f"Mobile: {d.get('mobile_no', 'N/A')}\n"
                        reply += f"Model: {d.get('vehicle_model', 'N/A')}\n"
                        reply += f"Fuel: {d.get('fuel_type', 'N/A')}\n"
                        reply += f"Reg Date: {d.get('regn_dt', 'N/A')}\n"
                        reply += f"Insurance Until: {d.get('ins_upto', 'N/A')}\n"
                    except requests.exceptions.RequestException as e:
                        reply = f"API fetch failed: {str(e)}"
                    except (KeyError, IndexError, json.JSONDecodeError) as e:
                        reply = f"Data parse error: {str(e)}. Invalid response or vehicle not found."
                    except Exception as e:
                        reply = f"Unexpected error: {str(e)}"
                else:
                    reply = "Invalid input. Send a valid vehicle number (min 8 chars, alphanumeric)."

                # Send reply to Telegram
                send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                payload = {"chat_id": chat_id, "text": reply}
                send_resp = requests.post(send_url, json=payload)
                if not send_resp.ok:
                    print(f"Telegram send failed: {send_resp.text}")  # For Vercel logs

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

        except Exception as e:
            print(f"Handler error: {str(e)}")  # Logs mein dikhega
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Internal Error: {str(e)}".encode())

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Webhook endpoint ready. Use POST for Telegram updates.")
