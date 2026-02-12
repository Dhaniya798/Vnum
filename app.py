import json
import os
import requests
from http.server import BaseHTTPRequestHandler

# Telegram Bot Token (Vercel env var se le)
TOKEN = os.environ.get('8355016420:AAFnAheJgoKgvQiOQ0J6dGMoIHowVC3mpcU')
API_BASE = "https://encorexapi.vercel.app/vehicletest?vnum="

if not TOKEN:
    raise ValueError("BOT_TOKEN not set in env vars")

WEBHOOK_PATH = f"/{TOKEN}"  # Telegram webhook yahin pe hit karega

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == WEBHOOK_PATH:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            update = json.loads(post_data)

            # Simple message handling
            if 'message' in update:
                chat_id = update['message']['chat']['id']
                text = update['message'].get('text', '').strip().upper()

                if text == '/start':
                    reply = "Vehicle lookup bot ready. Send vehicle number like RJ07CC8989"
                elif len(text) >= 8 and text.isalnum():  # Rough vehicle number check
                    try:
                        url = API_BASE + text
                        resp = requests.get(url, timeout=10).json()
                        d = resp["data"]["data"]["data"][0]

                        reply = f"Details for {text}:\n"
                        reply += f"Owner: {d.get('owner_name', 'N/A')}\n"
                        reply += f"Father: {d.get('father_name', 'N/A')}\n"
                        reply += f"Mobile: {d.get('mobile_no', 'N/A')}\n"
                        reply += f"Model: {d.get('vehicle_model', 'N/A')}\n"
                        reply += f"Fuel: {d.get('fuel_type', 'N/A')}\n"
                        reply += f"Reg Date: {d.get('regn_dt', 'N/A')}\n"
                        reply += f"Insurance: {d.get('ins_upto', 'N/A')}\n"
                    except Exception as e:
                        reply = f"Error: {str(e)}. Try again or check number."
                else:
                    reply = "Send valid vehicle number."

                # Send reply via Telegram API
                send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                payload = {"chat_id": chat_id, "text": reply}
                requests.post(send_url, json=payload)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()

# Vercel expects this for serverless
def handler_wrapper(environ, start_response):
    # Simple adapter for Vercel (WSGI-like)
    request = environ.get('REQUEST_METHOD', 'GET')
    if request == 'POST':
        # Simulate BaseHTTPRequestHandler for POST
        handler_instance = handler()
        handler_instance.path = environ['PATH_INFO']
        handler_instance.headers = {k.lower(): v for k, v in environ.items() if k.startswith('HTTP_')}
        # Call do_POST
        handler_instance.do_POST()
        start_response('200 OK', [('Content-type', 'text/plain')])
        return [b"OK"]
    else:
        start_response('405 Method Not Allowed', [('Content-type', 'text/plain')])
        return [b"Only POST allowed"]

# For local testing (optional)
if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, handler_wrapper)
    print("Local server on http://localhost:8000")
    httpd.serve_forever()
