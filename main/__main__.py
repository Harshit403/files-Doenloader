# main/__main__.py

import asyncio
import glob
import logging
from pathlib import Path
from telethon import TelegramClient
from pyrogram import Client

from . import (
    API_ID, API_HASH, BOT_TOKEN, LOGS,
    FORCESUB, MONGODB_URI, AUTH_USERS
)

# Initialize global clients
bot = TelegramClient("bot", API_ID, API_HASH)
Bot = Client("save-restricted-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Import after clients are defined (to avoid circular issues)
from .utils import load_plugins

logging.basicConfig(
    format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
    level=logging.WARNING
)

async def preload_dialogs():
    """Preload dialogs so Telethon can send to private LOGS channel."""
    if LOGS:
        try:
            await bot.get_dialogs(limit=100)
            logging.warning("Dialogs preloaded for LOGS channel access.")
        except Exception as e:
            logging.error("Failed to preload dialogs: %s", e)

async def main():
    # Start Telethon
    await bot.start(bot_token=BOT_TOKEN)
    logging.warning("Telethon bot started.")

    # Preload dialogs for LOGS
    await preload_dialogs()

    # Start Pyrogram
    await Bot.start()
    logging.warning("Pyrogram bot started.")

    # Load plugins (handlers)
    path = "main/plugins/*.py"
    files = glob.glob(path)
    for name in files:
        plugin_name = Path(name).stem
        load_plugins(plugin_name)

    logging.warning("Successfully deployed! Bot is running...")
    await asyncio.Event().wait()  # Keep alive

if __name__ == "__main__":
    asyncio.run(main())
