import os, time, asyncio, \
    requests, shutil, random, logging
from pyrogram.enums import MessageMediaType
from .. import bot as Drone, bot
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from .. import bot, API_ID, API_HASH, BOT_TOKEN, FORCESUB, ACCESS, FORCESUB, Bot
import os
from pyrogram.errors import ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid
from main.plugins.helpers import get_link, join, set_timer, check_timer, screenshot
from main.plugins.display_progress import progress_for_pyrogram
from main.Database.database import Database
from decouple import config
from telethon import Button
from telethon import events, Button
from telethon.tl.functions.users import GetFullUserRequest
from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest
from pyrogram.errors import FloodWait, BadRequest
from pyrogram import Client, filters, idle
import re, time, asyncio, logging
from PyHarshit.tg.extractor import videoMetaData
from PyHarshit.tg.Control import uploadFile

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

process=[]
timer=[]

async def check_user(id):
    ok = True
    try:
        await bot(GetParticipantRequest(channel=FORCESUB, participant=id))
        ok = True
    except UserNotParticipantError:
        ok = False
    return ok

async def get_msg(userbot, client, sender, msg_link, edit):
    chat = "" 
    round_message = False 
    msg_id = 0
    height, width, duration, thumb_path = 90, 90, 0, None
    try:
        await client.get_chat(sender)
    except:
        me = await client.get_me()
        await edit.edit(f"👀 You need to start a chat with @{me.username} first.")
        return None
    try:
        msg_id = int(msg_link.split("/")[-1])
    except ValueError:
        if '?single' in msg_link:
            link_ = msg_link.split("?single")[0]
            msg_id = int(link_.split("/")[-1])
        else:
            await edit.edit(f"🚫 Seems like you sent an unsupported link.")
            return None
    if 't.me/c/' in msg_link:
        st, r = check_timer(sender, process, timer) 
        if st == False:
            await Bot.send_message(sender, r) 
        if 't.me/b/' in msg_link:
            chat = str(msg_link.split("/")[-2])
        else:
            chat = int('-100' + str(msg_link.split("/")[-2]))
        file = ""
        try:
            try:
                msg = await userbot.get_messages(chat, msg_id)
            except FloodWait as f:
                await edit.edit(f'Bot is sleeping for {f.value} seconds due to telegram limitations.')
            except Exception as e:
                await edit.edit(e)
            if msg.media: 
                if msg.media == MessageMediaType.WEB_PAGE:
                    edit = await edit.edit('⏳')
                    await client.send_message(sender, msg.text.markdown)
                    me = await client.get_me()
                    await edit.edit(f'Your file has been forwarded to @{me.username}.')
                    #await set_timer(Bot, sender, process, timer)
                    return
            if not msg.media:
                if msg.text:
                    edit = await edit.edit("Forwarding...")
                    await client.send_message(sender, msg.text.markdown)
                    me = await client.get_me()
                    await edit.edit(f'Your file has been forwarded to @{me.username}.')
                    #await set_timer(Bot, sender, process, timer)
                    return
            edit = await edit.edit('Processing...')
            file = await userbot.download_media(
                msg,
                progress=progress_for_pyrogram,
                progress_args=(
                    userbot,
                    "🟢 Downloading:\n",
                    edit,
                    time.time()
                )
            )
            await edit.edit('⚪ Uploading...')
            caption = str(file)
            if msg.caption is not None:
                caption = msg.caption
            caption_entities = msg.caption_entities 
            if msg.media==MessageMediaType.VIDEO_NOTE: 
                 round_message = True 
                 print("Trying to get metadata") 
                 data = videoMetaData(file) 
                 height, width, duration = data["height"], data["width"], data["duration"] 
                 print(f'd: {duration}, w: {width}, h:{height}') 
                 try: 
                     thumb_path = await screenshot(file, duration, sender) 
                 except Exception: 
                     thumb_path = None 
                 await client.send_video_note( 
                     chat_id=sender, 
                     video_note=file, 
                     length=height, duration=duration,  
                     thumb=thumb_path, 
                     progress=progress_for_pyrogram, 
                     progress_args=( 
                         client, 
                         'Uploading...\n', 
                         edit, 
                         time.time() 
                     ) 
                 )
                 me = await client.get_me()
                 await edit.edit(f'Your file has been forwarded to @{me.username}.')
            #await set_timer(Bot, sender, process, timer)
            elif msg.media==MessageMediaType.VIDEO and msg.video.mime_type in ["video/mp4", "video/x-matroska"]:
                if str(file).split(".")[-1] in ['webm', 'mkv']:
                    path = str(file).split(".")[0] + ".mp4"
                    os.rename(file, path) 
                    file = str(file).split(".")[0] + ".mp4"
                data = videoMetaData(file)
                height, width, duration = data["height"], data["width"], data["duration"]
                print(f'd: {duration}, w: {width}, h:{height}')
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
                    await edit.delete()
                except:
                    pass
                me = await client.get_me()
                await Bot.send_message(sender, 'Your file has been forwarded to @{me.username}.')
                #await edit.edit(f'Your file has been forwarded to @{me.username}.')
                #await set_timer(Bot, sender, process, timer)
            elif str(file).split(".")[-1] in ['jpg', 'jpeg', 'png', 'webp']:
                await edit.edit("Uploading image file...")
                await client.send_photo(sender, file, caption=caption)
                me = await client.get_me()
                await edit.edit(f'Your file has been forwarded to @{me.username}.')
                #await set_timer(Bot, sender, process, timer)
            elif str(file).split(".")[-1] in ['mp3', 'ogg', 'wav', 'm4a', 'Flac', 'AAC']:
                await edit.edit("Uploading Audio File...")
                await client.send_audio(sender, file, caption=caption)
                me = await client.get_me()
                await edit.edit(f'Your file has been forwarded to @{me.username}.') 
                #await set_timer(Bot, sender, process, timer)
            else:
                await client.send_document(
                    sender,
                    file, 
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        client,
                        'Uploading...\n',
                        edit,
                        time.time()
                    )
                )
            me = await client.get_me()
            await edit.edit(f'Your file has been forwarded to @{me.username}.')
            #await set_timer(Bot, sender, process, timer)
            try:
                os.remove(file)
                if os.path.isfile(file) == True:
                    os.remove(file)
            except Exception:
                pass
            await edit.delete()
        except (ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid):
            await edit.edit("There is a problem in your source channel.")
            return
        except Exception as e:
            await edit.edit(e)
            return
            
    else:
        st, r = check_timer(sender, process, timer) 
        if st == False:
            await Bot.send_message(sender, r)
            return await edit.delete()
        chat =  msg_link.split("/")[-2]
        try:
            await client.copy_message(int(sender), chat, msg_id)
            me = await client.get_me()
            await edit.edit(f'Your file has been forwarded to @{me.username}.')
            await set_timer(Bot, sender, process, timer)
        except FloodWait as f: 
            return await edit.edit(f"Bot is limited by telegram for {f.value + 2} seconds.")
            await asyncio.sleep(f.value)
        except Exception as e:
            if "Empty messages cannot be copied" in str(e):
                group = await userbot.get_users(chat)
                group_link = f't.me/c/{int(group.id)}/{int(msg_id)}'
                return await get_msg(userbot, JVbot, bot, sender, edit_id, msg_link, i)
            else:
                print(e)
                return await edit.edit(sender, f'{str(e)}')
        except (ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid):
            await client.edit_message_text(sender, edit_id, "Send Invite Link First.")
        
@Bot.on_message(filters.private & filters.incoming)
async def clone(bot, event):
    try:
       link = get_link(event.text)
       if not link:
           return
    except TypeError:
        return
    try:
        edit = await event.reply('⏳')
    except Exception as e:
        await event.reply(f'Error: {e}')
    if not await check_user(event.chat.id):
        return await edit.edit(f"Hello {event.chat.first_name}, Due to overload only my channel subscribers can use me.\n\nPlease join my channel and then start me again!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel", url=f"https://t.me/{FORCESUB}")]]),)
    MONGODB_URI = config("MONGODB_URI", default=None)
    db = Database(MONGODB_URI, 'saverestricted')
    bot_token = await db.get_botCreds(event.chat.id)
    if bot_token:
        try:
            JVbot = Client(
                name=str(bot_token.split(":")[0]),
                api_hash=API_HASH,
                api_id=API_ID,
                bot_token=bot_token,
                in_memory=True)
            await JVbot.start()
        except ValueError:
            return await edit.edit("Your bot token is not valid, please /disconnect and /connect again.")
        except Exception as e:
            print(e)
            return await edit.edit(f'{str(e)}')
    else:
        return await edit.edit("⚠️Your bot is not connected yet.\nHit /connect to connect the bot.")
    if 't.me' in link and not 't.me/c/' in link and not 't.me/+' in link:
        try:
            await get_msg(bot, JVbot, event.chat.id, link, edit)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except ValueError as v:
            return await edit.edit(f'`{str(v)}`')
            await asyncio.sleep(2)
        except Exception as e:
            return await edit.edit(f'Error: `{str(e)}`')   
            await asyncio.sleep(2)      
        except FloodWait as e:
            return await edit.edit(f"Bot is limited by telegram for {e.value + 2} seconds.")

    userbot = ""
    i, h, s = await db.get_credentials(event.chat.id)
    if i and h and s is not None:
        try:
            userbot = Client(
                name=s[0:15],
                session_string=s,
                api_hash=h,
                api_id=int(i),
                in_memory=True)
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
    if 't.me/c' in link:
        try:
            await get_msg(userbot, JVbot, event.chat.id, link, edit)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception as e:
            return await edit.edit(f'Error: `{str(e)}`')
            await asyncio.sleep(2)         
        except (ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid):
            await edit.edit("Send Invite Link of your private chat first.")
            await asyncio.sleep(2)
