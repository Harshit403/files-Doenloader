

from main.Database.database import Database

from pyrogram import Client, filters, idle
from pyrogram.errors import FloodWait, BadRequest
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant

import asyncio, subprocess, re, os, time
from decouple import config

forcesub_text = 'You have to join @pyrogrammers to use this bot.'


#Multi client-------------------------------------------------------------------------------------------------------------

async def login(sender, i, h, s):
    MONGODB_URI = config("MONGODB_URI", default=None)
    db = Database(MONGODB_URI, 'saverestricted')
    await db.update_api_id(sender, i)
    await db.update_api_hash(sender, h)
    await db.update_session(sender, s)
    
async def connect(sender, i, h, t):
    MONGODB_URI = config("MONGODB_URI", default=None)
    db = Database(MONGODB_URI, 'saverestricted')
    await db.update_api_id(sender, i)
    await db.update_api_hash(sender, h)
    await db.update_token(sender, t)

async def logout(sender):
    MONGODB_URI = config("MONGODB_URI", default=None)
    db = Database(MONGODB_URI, 'saverestricted')
    await db.rem_api_id(sender)
    await db.rem_api_hash(sender)
    await db.rem_session(sender)
   
#Join private chat-------------------------------------------------------------------------------------------------------------

async def join(client, invite_link):
    try:
        await client.join_chat(invite_link)
        return "✅Channel joined Successfully."
        await asyncio.sleep(3)
    except FloodWait:
        return "FloodWait error, please try again later."
        await asyncio.sleep(3)
    except Exception as e:
        return f"❌Something went wrong."
        await asyncio.sleep(3)   
#forcesub-------------------------------------------------------------------------------------------------------------

async def forcesub(bot, sender):
    FORCESUB = config("FORCESUB", default=None)
    if not str(FORCESUB).startswith("-100"):
        FORCESUB = int("-100" + str(FORCESUB))
    try:
        user = await bot.get_chat_member(FORCESUB, sender)
        if user.status == "kicked":
            return True
    except UserNotParticipant:
        return True
    except Exception as e:
        print(e)
        return True
        
#Regex---------------------------------------------------------------------------------------------------------------
#to get the url from event

def get_link(string):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,string)   
    try:
        link = [x[0] for x in url][0]
        if link:
            return link
        else:
            return False
    except Exception:
        return False
    
#Anti-Spam---------------------------------------------------------------------------------------------------------------

#Set timer to avoid spam
async def set_timer(bot, sender, list1, list2):
    now = time.time()
    list2.append(f'{now}')
    list1.append(f'{sender}')
    await bot.send_message(sender, 'You can start a new process again after 11 minutes.\n__To overcome these limitations, please contact [@Pyro_owner](https://t.me/pyro_owner) to upgrade to the Premium Plan.__')
    await asyncio.sleep(660)
    list2.pop(int(list2.index(f'{now}')))
    list1.pop(int(list1.index(f'{sender}')))
    
#check time left in timer
def check_timer(sender, list1, list2):
    if f'{sender}' in list1:
        index = list1.index(f'{sender}')
        last = list2[int(index)]
        present = time.time()
        return False, f"Please wait {660-round(present-float(last))} seconds to get next message.\n__To overcome these limitations, please contact [@Pyro_owner](https://t.me/pyro_owner) to upgrade to the Premium Plan.__"
    else:
        return True, None

#Screenshot---------------------------------------------------------------------------------------------------------------

async def screenshot(video, time_stamp, sender):
    if os.path.isfile(f'{sender}.jpg'):
        return f'{sender}.jpg'
    out = str(video).split(".")[0] + ".jpg"
    cmd = (f"ffmpeg -ss {time_stamp} -i {video} -vframes 1 {out}").split(" ")
    process = await asyncio.create_subprocess_exec(
         *cmd,
         stdout=asyncio.subprocess.PIPE,
         stderr=asyncio.subprocess.PIPE)
        
    stdout, stderr = await process.communicate()
    x = stderr.decode().strip()
    y = stdout.decode().strip()
    print(x)
    print(y)
    if os.path.isfile(out):
        return out
    else:
        None
        
        
        
