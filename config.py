import os
from dotenv import load_dotenv

# .env faylni yuklash
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SUPER_ADMIN = int(os.getenv("SUPER_ADMIN"))