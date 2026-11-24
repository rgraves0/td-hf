import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from config import Config, DYNAMIC_VARS

from .tgclient import aio
from .helpers.database.pg_impl import set_db


class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running!")

    # Console ထဲမှာ HTTP request log တွေ မရှုပ်နေအောင် ပိတ်ထားခြင်း
    def log_message(self, format, *args):
        return


def run_web_server():
    # Hosting platform က ပေးတဲ့ PORT ကို ယူသုံးမည် (မရှိပါက 8000 ကို သုံးမည်)
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()


def load_dynamic_vars():
    for var in DYNAMIC_VARS:
        if not getattr(Config, var):
            setattr(Config, var, set_db.get_variable(var)[0])


if __name__ == "__main__":
    # Web Service Health Check အတွက် Background Thread ဖြင့် Server စတင်ခြင်း
    threading.Thread(target=run_web_server, daemon=True).start()

    if not os.path.isdir(Config.DOWNLOAD_BASE_DIR):
        os.makedirs(Config.DOWNLOAD_BASE_DIR)
    load_dynamic_vars()
    aio.run()
