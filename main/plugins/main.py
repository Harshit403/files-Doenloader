#pyrogrammers
#shit
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
#end shit
import logging, time, sys
import os, time, asyncio, \
    requests, shutil, random, logging
from pyrogram.enums import MessageMediaType
from .. import bot as Drone
#from pyromod import listen
from telethon import events, Button, errors, functions
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
#end
from .. import bot
import os
from main.plugins.helpers import get_link, forcesub, forcesub_text, join, set_timer, check_timer, screenshot
from main.plugins.display_progress import progress_for_pyrogram
from main.Database.database import Database
from decouple import config
from telethon import Button
API_ID = config("API_ID", default=None, cast=int)
API_HASH = config("API_HASH", default=None)
BOT_TOKEN = config("BOT_TOKEN", default=None)
FORCESUB = config("FORCESUB", default=None) 
ACCESS = config("ACCESS", default=None, cast=int)
#What the hell is it??
from telethon import events, Button
from telethon.tl.functions.users import GetFullUserRequest
from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest
#end
from pyrogram.errors import FloodWait, BadRequest
from pyrogram import Client, filters, idle
#from ethon.pyfunc import video_metadata

import re, time, asyncio, logging

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

process=[]
timer=[]

# join checks
async def check_user(id):
    ok = True
    try:
        await Drone(
            functions.channels.GetParticipantRequest(
                channel="pyrogrammers", participant=id
            )
        )
        ok = True
    except errors.rpcerrorlist.UserNotParticipantError:
        ok = False
    return ok

Bot = Client(
    "save-restricted-bot",
    bot_token=BOT_TOKEN,
    api_id=int(API_ID),
    api_hash=API_HASH
)

try:
    Bot.start()
except Exception as e:
    print(e)
    sys.exit(1)

errorC = """How fool is it?\nYou sent me invalid session string.\nHit /logout and /login again with valid pyrogram session string.Hit **Session Button** to generate session string."""

async def get_msg(userbot, client, sender, msg_link, edit):
    chat = ""
    msg_id = 0
    try:
        msg_id = int(msg_link.split("/")[-1])
    except ValueError:
        if '?single' in msg_link:
            link_ = msg_link.split("?single")[0]
            msg_id = int(link_.split("/")[-1])
        else:
            await edit.edit(f"🚫 Seems like you sent an unsupported message link.")
            return None
    if 't.me/c/' in msg_link:
        st, r = check_timer(sender, process, timer) 
        if st == False:
            return await edit.edit(r) 
        chat = int('-100' + str(msg_link.split("/")[-2]))
        try:
            msg = await userbot.get_messages(chat, msg_id)
###########madharxgod
            if msg.media:
                if msg.media == MessageMediaType.WEB_PAGE:
                    edit = await client.edit_message_text(sender, edit_id, "⚡")
                    await client.send_message(sender, msg.text.markdown)
                    await edit.delete()
                    return
            if not msg.media:
                if msg.text:
                    #edit = await client.edit_message_text(sender, edit_id, "⏳")
                    await client.send_message(sender, msg.text.markdown)
                    await edit.delete()
                    return
                if msg.empty or msg.service or msg.dice or msg.location:
                    edit = await client.edit_message_text(sender, edit_id, "This message doesn't exist.")
                    return 
################madharchod
            edit = await edit.edit('Processing...')
#end
            file = await userbot.download_media(
                msg,
                progress=progress_for_pyrogram,
                progress_args=(
                    userbot,
                    "**Downloading:**\n",
                    edit,
                    time.time()
                )
            )
            await edit.edit('UploadinG...')
            caption = str(file)
            if msg.caption is not None:
                caption = msg.caption
            if str(file).split(".")[-1] in ['mkv', 'mp4', 'webm']:
                if str(file).split(".")[-1] in ['webm', 'mkv']:
                    path = str(file).split(".")[0] + ".mp4"
                    os.rename(file, path) 
                    file = str(file).split(".")[0] + ".mp4"
#                data = video_metadata(file)
#                duration = data["duration"]
#mffff
                metadata = extractMetadata(createParser(file))
                duration = 0
                if metadata.has("duration"):
                    duration = metadata.get('duration').seconds
                width = 0
                height = 0
#mffff
                thumb_path = await screenshot(file, duration/2, sender)
                await client.send_video(
                    chat_id=sender,
                    video=file,
                    caption=caption,
                    supports_streaming=True,
                    duration=duration,
                    thumb=thumb_path,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        client,
                        '**Uploading:**\n',
                        edit,
                        time.time()
                    )
                )
            elif str(file).split(".")[-1] in ['jpg', 'jpeg', 'png', 'webp']:
                await edit.edit("Uploading image file...")
                await bot.send_file(sender, file, caption=caption)
                await edit.delete()
                await set_timer(client, sender, process, timer)
                #for audio
            elif str(file).split(".")[-1] in ['mp3', 'ogg', 'wav', 'm4a', 'Flac', 'AAC']:
                
                
                await edit.edit("Uploading Audio File...")
                await client.send_audio(sender, file, caption=caption)
                await edit.delete() 
                await set_timer(client, sender, process, timer)
            else:
                await client.send_document(
                    sender,
                    file, 
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        client,
                        '<b><u>Uploading...</b></u>\n',
                        edit,
                        time.time()
                    )
                )
            await edit.delete()
            await set_timer(client, sender, process, timer) 
        except Exception as e:
            if '400 CHANNEL_INVALID' in str(e):
                await edit.edit(F"You haven't joined this channel yet, please join this channel first then send me message link to save.")
            else:
                await edit.edit(F'ERROR: {str(e)}')
                return 
    else:
        st, r = check_timer(sender, process, timer) 
        if st == False:
            await client.send_message(sender, r)
            return await edit.delete()
        chat =  msg_link.split("/")[-2]
        try:
            await client.copy_message(int(sender), chat, msg_id)
            #text = "File has been copied to your saved messages.\nClick on Below Button."
            #reply_markup = InlineKeyboardMarkup(
            #[[InlineKeyboardButton(text="Show File", url=f"tg://openmessage?user_id={event.chat.id}")]]
            #)
            #await client.reply(event.chat.id, text, reply_markup=reply_markup)
            await edit.delete()
            await set_timer(client, sender, process, timer)
        except FloodWait as f:
            try: 
                await get_msg(userbot, bot, sender, msg_link, edit)
            except Exception as e:
                print(e) 
                return await edit.edit(f"Bot is limited by telegram for {f.value + 2} seconds.\nPlease wait until then or use @saverestrictedcontentsbot if working.")
                await asyncio.sleep(f.value)
        except Exception as e:
 #shit fuck code🤣
            if "empty" in {str(e)}:
                await get_msg(userbot, bot, sender, msg_link, edit)
            else:
#fuck off slut
                print(e)
                return await edit.edit(sender, f'{str(e)}')
        except BadRequest.CHANNEL_INVALID:
            return await edit.edit('Your Channel is unavailable.')
        except BadRequest.CHANNEL_PRIVATE:
            return await edit.edit('You have not joined the channel yet!.')
        
    
        
#@Bot.on_message(filters.private & filters.incoming)
@Drone.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def clone(event):
#async def clone(bot, event):
    try:
       link = get_link(event.text)
       if not link:
           return
    except TypeError:
        return
    if not await check_user(event.sender_id):
        return await event.reply(f"You have to join my channel in order to use.\n\nDue to overload only my channel subscribers can use me.", buttons=[Button.url("Join Channel", url="https://t.me/pyrogrammers")])
    edit = await event.reply("Initiating...")
    if 't.me' in link and not 't.me/c/' in link and not 't.me/+' in link:
        try:
            await get_msg(bot, plient, event.chat.id, link, edit)
        except FloodWait as e:
            return await edit.edit(f'Error: `{str(e)}`')
            await asyncio.sleep(e.value)
#        except ValueError as v:
#            return await edit.edit(f'`{str(v)}` Please send only message link, i can only save t.me types of links in free version.')
            await asyncio.sleep(2)
        except Exception as e:
            return await edit.edit(f'Error: `{str(e)}`')   
            await asyncio.sleep(2)      
        except FloodWait as e:
            return await edit.edit(f"Bot is limited by telegram for {e.value + 2} seconds.\nPlease wait until then or use @saverestrictedcontentsbot if working.")
#mfffff
        except ValueError:
            if '?single' in msg_link:
                link_ = msg_link.split("?single")[0]
                msg_id = int(link_.split("/")[-1])
            else:
                await edit.edit(f"🚫 Seems like you sent an unsupported message link.")
                return None
#mfffff
    userbot = ""
    MONGODB_URI = config("MONGODB_URI", default=None)
    db = Database(MONGODB_URI, 'saverestricted')
    i, h, s = await db.get_credentials(event.chat.id)
    if i and h and s is not None:
        try:
            userbot = Client(
                name="saverestricted",
                session_string=s, 
                api_hash=h,
                api_id=int(i))
            await userbot.start()
        except ValueError:
            return await edit.edit("Your login cridentials are not valid, please /logout and /login again.")
        except Exception as e:
            print(e)
            return await edit.edit(f'{str(e)}')
    else:
        return await edit.edit("⚠️You are not logged in.\nHit /login to log in to the bot.")
#bot
        plient = ""
        MONGODB_URI = config("MONGODB_URI", default=None)
        db = Database(MONGODB_URI, 'saverestricted')
        i, h, t = await db.get_credentials(event.chat.id)
        if i and h and t is not None:
            try:
                plient = Client(
                       "save-restricted-bot",
                       bot_token=t,
                       api_id=int(i),
                       api_hash=h
                )
            await plient.start()
            except ValueError:
                return await edit.edit("Your bot token not found please /connectbot again.")
            except Exception as e:
                print(e)
                return await edit.edit(f'{str(e)}')
        else:
             return await edit.edit("Please /connectbot first.")

#end bot 
    if 't.me/+' in link:
        xy = await join(userbot, link)
        await edit.edit(xy)
        return 
    if 't.me/c' in link:
        try:
            await get_msg(userbot, plient, event.chat.id, link, edit)
        except BadRequest.CHANNEL_INVALID:
            return await edit.edit('Join the channel first.')
            await asyncio.sleep(2)
        except FloodWait as e:
            return await edit.edit(f'Error: `{str(e)}`')
            await asyncio.sleep(e.value)
        except Exception as e:
            return await edit.edit(f'Error: `{str(e)}`')
            await asyncio.sleep(2)         
        except BadRequest.CHANNEL_PRIVATE:
            return await edit.edit('Join the channel first.')
            await asyncio.sleep(2)
