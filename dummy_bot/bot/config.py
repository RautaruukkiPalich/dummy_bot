import os
from dotenv import load_dotenv

load_dotenv()

HOST_ADD = os.environ.get("HOST_ADD", "web")
HOST_PORT = os.environ.get("HOST_PORT", 8080)
HOST_URL = f"http://{HOST_ADD}:{HOST_PORT}"
TOKEN = str(os.environ.get("TG_TOKEN"))
