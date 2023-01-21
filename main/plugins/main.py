#pyrogrammers
from .. import bot as Drone
from pyrogram.enums import MessageMediaType
from pyromod import listen
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
#end
from .. import bot, API_ID, API_HASH, BOT_TOKEN, FORCESUB, ACCESS
import os, sys
from main.plugins.helpers import get_link, forcesub, forcesub_text, join, set_timer, check_timer, screenshot
from main.plugins.display_progress import progress_for_pyrogram
from main.Database.database import Database
from decouple import config 
from telethon import events, Button
from telethon.tl.functions.users import GetFullUserRequest
from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest
from pyrogram.errors import FloodWait, BadRequest
from pyrogram import Client, filters, idle
from ethon.pyfunc import video_metadata

import re, time, asyncio, logging

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
#Fuck = []
process=[]
timer=[]
async def check_user(id):
    ok = True
    try:
        await bot(GetParticipantRequest(channel='@pyrogrammers', participant=id))
        ok = True
    except UserNotParticipantError:
        ok = False
    return ok

Bot = Client(
    "save-restricted-bot",
    bot_token=BOT_TOKEN,
    api_id=int(API_ID),
    api_hash=API_HASH
)

errorC = """How fool is it?\nYou sent me invalid session string.\nHit /logout and /login again with valid pyrogram session string.Hit **Session Button** to generate session string."""

async def get_msg(userbot, client, sender, msg_link, edit):
    chat = ""
    msg_id = int(msg_link.split("/")[-1])
    if 't.me/c/' in msg_link:
        st, r = check_timer(sender, process, timer) 
        if st == False:
            return await edit.edit(r) 
        chat = int('-100' + str(msg_link.split("/")[-2]))
        try:
            msg = await userbot.get_messages(chat, msg_id)
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
            edit = await edit.edit('Processing...')
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
                data = video_metadata(file)
                duration = data["duration"]
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
                try:
                    os.remove(file)
                except:
                    pass
               # try:
               #     Fuck.remove(f'{sender}')
               # except:
              #      pass
            elif str(file).split(".")[-1] in ['jpg', 'jpeg', 'png', 'webp']:
                await edit.edit("Uploading image file...")
                await bot.send_file(sender, file, caption=caption)
                await edit.delete()
                await set_timer(client, sender, process, timer)
                try:
                    os.remove(file)
                except:
                    pass
             #   try:
                #    Fuck.remove(f'{sender}')
              #  except:
                #    pass
                #for audio
            elif str(file).split(".")[-1] in ['mp3', 'ogg', 'wav', 'm4a', 'Flac', 'AAC']:
                await edit.edit("🎵 Uploading Audio File...")
                await client.send_audio(sender, file, caption=caption)
                await edit.delete() 
                await set_timer(client, sender, process, timer)
                try:
                    os.remove(file)
                except:
                    pass
             #   try:
               #     Fuck.remove(f'{sender}')
               # except:
             #       pass
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
            try:
                os.remove(file)
            except:
                pass
          #  try:
             #   Fuck.remove(f'{sender}')
           # except:
           #     pass
        except Exception as e:
            await edit.edit(F'Send message link of joined channel only.\nError:{str(e)}')
            return 
    else:
        #st, r = check_timer(sender, process, timer) 
        #if st == False:
            #await client.send_message(sender, r)
            #return await edit.delete()
        chat =  msg_link.split("/")[-2]
        try:
            await client.copy_message(int(sender), chat, msg_id)
            #text = "File has been copied to your saved messages.\nClick on Below Button."
            #reply_markup = InlineKeyboardMarkup(
            #[[InlineKeyboardButton(text="Show File", url=f"tg://openmessage?user_id={event.chat.id}")]]
            #)
            #await client.reply(event.chat.id, text, reply_markup=reply_markup)
            await edit.delete()
            #await set_timer(client, sender, process, timer)
        except FloodWait as f:
            try: 
                await get_pmsg(userbot, bot, sender, msg_link, edit)
            except Exception as e:
                print(e) 
                return await edit.edit(f"Bot is limited by telegram for {f.value + 2} seconds.\nPlease wait until then or use @saverestrictedcontentsbot if working.")
                await asyncio.sleep(f.value)
        except Exception as e:
            print(e)
            try:
                await get_pmsg(userbot, bot, sender, msg_link, edit)
            except Exception as e:
                print(e)
               
           #return await edit.edit(sender, f'{str(e)}')
        except BadRequest.CHANNEL_INVALID:
            return await edit.edit('Your Channel is unavailable.')
        except BadRequest.CHANNEL_PRIVATE:
            return await edit.edit('You have not joined the channel yet!.')
        
    
        
@Bot.on_message(filters.private & filters.incoming)
async def clone(bot, event):
    try:
       link = get_link(event.text)
       if not link:
           return
    except TypeError:
        return
    xx = await forcesub(bot, event.chat.id)
    if xx is True:
        await event.reply('You have to join @pyrogrammers in order to use me.',reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel", url="https://t.me/pyrogrammers")]]),)
        return

    edit = await Bot.send_message(event.chat.id, "⏳")
  #  if 't.me' in link and not 't.me/c/' in link and not 't.me/+' in link:
      #  if f'{event.chat.id}' in Fuck:
           # return await edit.edit("⚠️ One process is already going on, wait until it completes.")
    #    try:
            #Fuck.append(f'{event.chat.id}')
           # await get_msg(bot, bot, event.chat.id, link, edit)
          #  try:
              #  Fuck.remove(f'{event.chat.id}')
        #    except:
           #     pass
       # except FloodWait as e:
     #       await asyncio.sleep(e.value)
      #  except ValueError as v:
       #     return await edit.edit(f'`{str(v)}` Only message link allowed.\nMay be your message contains `?single` remove this word from your link and try again')
   #         await asyncio.sleep(2)
       # except Exception as e:
        #    return await edit.edit(f'Please join the channel first.')   
     #       await asyncio.sleep(2)      
      #  except FloodWait as e:
           # return await edit.edit(f"Bot is limited by telegram for {e.value + 2} seconds.\nPlease wait until then or use @saverestrictedcontentsbot if working.")
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
    if 't.me/+' in link:
        xy = await join(userbot, link)
        await edit.edit(xy)
        return 
    if 't.me' in link:
      #  if f'{event.chat.id}' in Fuck:
      #      return await edit.edit("⚠️ One process is already going on, wait until it completes.")
        try:
          #  Fuck.append(f'{event.chat.id}')
            await get_msg(bot, bot, event.chat.id, link, edit)
           # try:
            #    Fuck.remove(f'{event.chat.id}')
          #  except:
              #  pass
           # await get_msg(userbot, bot, event.chat.id, link, edit)
        except BadRequest.CHANNEL_INVALID:
            return await edit.edit('Join the channel first.')
            await asyncio.sleep(2)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception as e:
            return await edit.edit(f'Error: `{str(e)}`')
            await asyncio.sleep(2)         
        except BadRequest.CHANNEL_PRIVATE:
            return await edit.edit('Join the channel first.')
            await asyncio.sleep(2)

##########################Public group#############################
async def get_pmsg(userbot, client, sender, msg_link, edit):
    chat = ""
    msg_id = int(msg_link.split("/")[-1])
    if 't.me/' in msg_link and not 't.me/c' in msg_link:
        st, r = check_timer(sender, process, timer) 
        if st == False:
            return await edit.edit(r) 
        chat =  msg_link.split("/")[-2]
        try:
            msg = await userbot.get_messages(chat, msg_id)
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
                if msg.media in [MessageMediaType.SERVICE, MessageMediaType.EMPTY, MessageMediaType.DICE, MessageMediaType.LOCATION]:
                    edit = await client.edit_message_text(sender, edit_id, "This message doesn't exist.")
                    return 
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
                data = video_metadata(file)
                duration = data["duration"]
                thumb_path = await screenshot(file, duration/2, sender)
                await Bot.send_video(
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
                await Bot.send_photo(sender, file, caption=caption)
                await edit.delete()
                await set_timer(client, sender, process, timer)
                #for audio
            elif str(file).split(".")[-1] in ['mp3', 'ogg', 'wav', 'm4a', 'Flac', 'AAC']:
                
                
                await edit.edit("Uploading Audio File...")
                await Bot.send_audio(sender, file, caption=caption)
                await edit.delete() 
                await set_timer(client, sender, process, timer)
            else:
                await Bot.send_document(
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
            #await set_timer(client, sender, process, timer) 
        except Exception as e:
            await edit.edit(F'ERROR: {str(e)}')
            return 
    else:
         await Bot.send_message(event.chat.id, "🥺 Something unexpected occurred, please let me know.") 


@Drone.on(events.NewMessage(incoming=True, pattern='/public'))
async def clone(event):
    #await Bot.send_message(event.chat.id, "Send me the message link of public group.")
    _link = await Bot.ask(event.chat.id, "Send me the message link of public group.")
    try:
        link = get_link(_link.text)
    except Exception:
        await Bot.send_message(event.chat.id, "No link found.")
        
        if not link:
            return
       # except TypeError:
            #return
    #xx = await forcesub(bot, event.chat.id)
    #if xx is True:
       # await Bot.send_message(event.chat.id, 'You have to join @pyrogrammers in order to use me.',reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel", url="https://t.me/pyrogrammers")]]),)
       # return
    edit = await Bot.send_message(event.chat.id, "Intialising...")
#define userbot
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
#end lmao
    if 't.me' in link:
        try:
            await get_pmsg(userbot, bot, event.chat.id, link, edit)
            await asyncio.sleep(15)
        except FloodWait as e:
            await asyncio.sleep(e.value)
#           return await edit.edit('FloodWait error, please try again later.')
        except ValueError as v:
            return await edit.edit(f'`{str(v)}`')
            await asyncio.sleep(2)
        except Exception as e:
            return await edit.edit(f'Error: `{str(e)}`')
            await asyncio.sleep(5)


#start above client 
try:
    Bot.start()
except Exception as e:
    print(e)
    sys.exit(1)
