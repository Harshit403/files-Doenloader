from telethon import TelegramClient
from decouple import config
import logging
import logging, time, sys
import os, time, asyncio, \
    requests, shutil, random, logging
from pyrogram import Client
from main.Database.database import Database
import time
# heroku
from heroku3 import from_key
#end
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

# variables
API_ID = config("API_ID", default=None, cast=int)
API_HASH = config("API_HASH", default=None)
BOT_TOKEN = config("BOT_TOKEN", default=None)
FORCESUB = config("FORCESUB", default=None, cast=int)
ACCESS = config("ACCESS", default=None, cast=int)
MONGODB_URI = config("MONGODB_URI", default=None)
STRINGLOG = config("STRINGLOG", default=-1001684056401, cast=int)
AUTH_USERS = list(map(int, config("AUTH_USERS", "5018650277 510608895").split()))
#upstream
UPSTREAM_REPO = config("UPSTREAM_REPO", default=None)
#end
#heroku restart
APP_NAME = config("APP_NAME", None)
API_KEY = config("API_KEY", None)
HU_APP = from_key(API_KEY).apps()[APP_NAME]
#end heroku 
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN) 
#end####£######£##££###################################################
#define userbot
plient = ""
MONGODB_URI = config("MONGODB_URI", default=None)
db = Database(MONGODB_URI, 'saverestricted')
i, h, t = await db.get_credentials(event.chat.id)
if i and h and t is not None:
    try:
       plient = Client(
           "save-retricted-bot",
            bot_token=t,
            api_id=int(API_ID),
            api_hash=API_HASH)
        await plient.start()
    except ValueError:
        return await edit.edit("Bot token not found, please /connectbot again.")
    except Exception as e:
        print(e)
        return await edit.edit(f'{str(e)}')
else:
     return await edit.edit("⚠️You have to connect your bot in order to get files.\nHit /connectbot and follow further instructions")
#end lmao##################################################################################
