import os
import json
import time
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

def telegram(method, data=None):
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    body = json.dumps(data or {}).encode()
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=40) as response:
        return json.loads(response.read().decode())

def listen():
    offset = None
    while True:
        try:
            params = {"timeout": 25}
            if offset is not None:
                params["offset"] = offset

            result = telegram("getUpdates", params)

            for update in result.get("result", []):
                offset = update["update_id"] + 1
                message = update.get("message", {})
                chat_id = message.get("chat", {}).get("id")
                command = message.get("text", "")

                if chat_id and command in ("/start", "/test"):
                    telegram("sendMessage", {
                        "chat_id": chat_id,
                        "text": "¡Radar BTC Kalshi conectado! Mensaje de prueba recibido. Modo simulado: no realiza operaciones."
                    })
        except Exception:
            time.sleep(5)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Radar BTC Kalshi activo")

    def log_message(self, *args):
        pass

if not TOKEN:
    raise RuntimeError("Falta configurar TELEGRAM_BOT_TOKEN")

threading.Thread(target=listen, daemon=True).start()

port = int(os.environ.get("PORT", "10000"))
HTTPServer(("0.0.0.0", port), Handler).serve_forever()
