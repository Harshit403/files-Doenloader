# main/__main__.py

import glob
from pathlib import Path
from main.utils import load_plugins
import logging
from . import bot, LOGS

logging.basicConfig(
    format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
    level=logging.WARNING
)

async def preload_dialogs():
    """Preload dialogs so LOGS channel is cached."""
    if LOGS:
        try:
            await bot.get_dialogs(limit=100)
            logging.warning("📥 Dialogs preloaded for LOGS channel.")
        except Exception as e:
            logging.error("⚠️ Failed to preload dialogs: %s", e)

# Load plugins
path = "main/plugins/*.py"
files = glob.glob(path)
for name in files:
    with open(name) as a:
        patt = Path(a.name)
        plugin_name = patt.stem
        load_plugins(plugin_name)

print("Successfully deployed!")

# Start bot and preload
with bot:
    bot.loop.run_until_complete(preload_dialogs())
    bot.run_until_disconnected()
