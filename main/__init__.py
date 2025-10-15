# main/__init__.py

import os
import sys
import logging
import asyncio
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
API_ID = getenv_int("API_ID", 4680197)
API_HASH = os.getenv("API_HASH", "495b0228624028d635bd748b22985f67")
BOT_TOKEN = os.getenv("BOT_TOKEN")
FORCESUB = os.getenv("FORCESUB")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://itsharshit_db_user:QJhxnouQBv07eLcB@cluster0.hcrawmw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
LOGS = getenv_int("LOGS")
AUTH_USERS = getenv_int_list("AUTH_USERS", [7477152489])  # Ensure it's a list

# ---------- sanity checks ----------
if not all([API_ID, API_HASH, BOT_TOKEN]):
    logging.error("Missing critical environment variables (API_ID/HASH/BOT_TOKEN)")
    sys.exit(1)

# ---------- Telethon client ----------
bot = TelegramClient("bot", API_ID, API_HASH)

# Start the bot
async def start_telethon():
    await bot.start(bot_token=BOT_TOKEN)
    # ✅ Critical: Preload dialogs to cache private channels (like LOGS)
    try:
        await bot.get_dialogs(limit=100)
        logging.warning("✅ Telethon dialogs preloaded – entity cache ready.")
    except Exception as e:
        logging.error("⚠️ Failed to preload dialogs: %s", e)

# Run Telethon startup
asyncio.create_task(start_telethon())

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
logging.warning("✅ Both Telethon and Pyrogram clients started successfully.")
