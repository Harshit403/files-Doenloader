import asyncio
import glob
import logging
from pathlib import Path
from telethon import TelegramClient
from pyrogram import Client

from . import API_ID, API_HASH, BOT_TOKEN, LOGS

# ✅ Create and assign global 'bot' BEFORE importing plugins
bot = TelegramClient("bot", API_ID, API_HASH)
Bot = Client("save-restricted-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Make them available for imports (patch into package namespace)
import sys
sys.modules['main'].bot = bot
sys.modules['main'].Bot = Bot

from .utils import load_plugins

logging.basicConfig(
    format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
    level=logging.WARNING
)

async def preload_dialogs():
    if LOGS:
        try:
            await bot.get_dialogs(limit=100)
            logging.warning("Dialogs preloaded.")
        except Exception as e:
            logging.error("Failed to preload dialogs: %s", e)

async def main():
    # Start clients
    await bot.start(bot_token=BOT_TOKEN)
    await preload_dialogs()
    await Bot.start()
    logging.warning("Bots started.")

    # Load plugins AFTER clients exist
    path = "main/plugins/*.py"
    for name in glob.glob(path):
        plugin_name = Path(name).stem
        load_plugins(plugin_name)

    logging.warning("Successfully deployed!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
