import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # e.g., -1001234567890
GROUP_ID = os.getenv("GROUP_ID")      # e.g., -1009876543210