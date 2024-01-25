import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = str(os.environ.get("TG_TOKEN"))

HOST_ADD = os.environ.get("HOST_ADD", "web")
HOST_PORT = os.environ.get("HOST_PORT", 8080)
HOST_URL = f"http://{HOST_ADD}:{HOST_PORT}"

DB_NAME = os.environ.get('DB_NAME', 'postgres')
DB_HOST = os.environ.get('DB_HOST', 'database')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASS = os.environ.get('DB_PASS', 'postgres')

DB_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
