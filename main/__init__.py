import os
import sys
import logging
from telethon import TelegramClient
from pyrogram import Client
from dotenv import load_dotenv

# ---------- logging ----------
logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.WARNING
)

# ---------- load env ----------
load_dotenv()

# ---------- helpers ----------
def getenv_int(key: str, default=None) -> int | None:
    val = os.getenv(key, default)
    try:
        return int(val) if val is not None else None
    except (ValueError, TypeError):
        return default

def getenv_int_list(key: str, default=None) -> list[int]:
    raw = os.getenv(key)
    if not raw:
        return default or []
    return [int(u.strip()) for u in raw.split() if u.strip().isdigit()]

# ---------- variables ----------
API_ID          = getenv_int("API_ID")
API_HASH        = os.getenv("API_HASH")
BOT_TOKEN       = os.getenv("BOT_TOKEN")
FORCESUB        = os.getenv("FORCESUB")
ACCESS          = getenv_int("ACCESS")
MONGODB_URI     = os.getenv("MONGODB_URI")
STRINGLOG       = getenv_int("STRINGLOG", -1001790160966)
AUTH_USERS      = getenv_int_list("AUTH_USERS")

# ---------- sanity checks ----------
if not all([API_ID, API_HASH, BOT_TOKEN]):
    logging.error("Missing critical environment variables (API_ID/HASH/BOT_TOKEN)")
    sys.exit(1)

# ---------- Telethon client ----------
bot = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ---------- Pyrogram client ----------
try:
    Bot = Client(
        "save-restricted-bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN
    )
    Bot.start()
except Exception as exc:
    logging.exception("Pyrogram client failed to start: %s", exc)
    sys.exit(1)

# ---------- ready ----------
logging.warning("Both clients started successfully.")
