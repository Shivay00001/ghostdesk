import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
    ALLOWED_USERS = [
        uid.strip() for uid in os.getenv("ALLOWED_USERS", "").split(",") if uid.strip()
    ]
    SYSTEM_NAME = "GhostDesk"

    @classmethod
    def validate(cls):
        if not cls.TELEGRAM_TOKEN:
            raise ValueError("Missing TELEGRAM_TOKEN in .env")
        if not cls.ALLOWED_USERS:
            print("WARNING: No ALLOWED_USERS defined. The bot will reject everyone.")
