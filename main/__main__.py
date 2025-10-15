# main/__main__.py

import glob
from pathlib import Path
from main.utils import load_plugins
import logging
from . import bot, Bot, LOGS, BOT_TOKEN  # ← import BOT_TOKEN

logging.basicConfig(
    format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
    level=logging.WARNING
)

async def preload_entities():
    if LOGS:
        try:
            await bot.get_dialogs(limit=100)
            logging.warning("📥 Dialogs preloaded for LOGS channel.")
        except Exception as e:
            logging.error("⚠️ Failed to preload dialogs: %s", e)

"""
async def start_pyrogram():
    try:
        await Bot.start()
        me = await Bot.get_me()
        logging.warning(f"✅ Pyrogram bot started as @{me.username}")
    except Exception as e:
        logging.error("❌ Failed to start Pyrogram bot: %s", e)
"""
# Load plugins
path = "main/plugins/*.py"
files = glob.glob(path)
for name in files:
    with open(name) as f:
        patt = Path(f.name)
        plugin_name = patt.stem
        load_plugins(plugin_name)

print("✅ Successfully deployed!")

# Start Telethon with BOT_TOKEN
with bot:
    bot.start(bot_token=BOT_TOKEN)  # ✅ Use the token from config

    bot.loop.run_until_complete(preload_entities())
    bot.loop.run_until_complete(start_pyrogram())

    bot.run_until_disconnected()
