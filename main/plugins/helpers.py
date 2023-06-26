from main.Database.database import Database
from pyrogram import Client, filters, idle
from pyrogram.errors import FloodWait, BadRequest
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
import asyncio, subprocess, re, os, time
from decouple import config

#Multi client-------------------------------------------------------------------------------------------------------------
async def login(sender, i, h, s):
    MONGODB_URI = config("MONGODB_URI", default=None)
    db = Database(MONGODB_URI, 'saverestricted')
    await db.update_api_id(sender, i)
    await db.update_api_hash(sender, h)
    await db.update_session(sender, s)
    
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
    except FloodWait as f:
        return f"Bot is limited by telegram for {f.value} seconds."
        await asyncio.sleep(f.value)
    except Exception as e:
        print(e)
        return f"❌Something went wrong."
        await asyncio.sleep(3)   
        
        
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
    fuck = await bot.send_message(sender, '`Bot is sleeping for 23 seconds to avoid telegram limitations.`')
    await asyncio.sleep(25)
    await fuck.edit('`Now you can forward a new message again.`')
    list2.pop(int(list2.index(f'{now}')))
    list1.pop(int(list1.index(f'{sender}')))
    
#check time left in timer
def check_timer(sender, list1, list2):
    if f'{sender}' in list1:
        index = list1.index(f'{sender}')
        last = list2[int(index)]
        present = time.time()
        return False, f"Please wait {24-round(present-float(last))} seconds to forward a new message."
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
        
        
        
