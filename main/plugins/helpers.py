import os, time, asyncio, subprocess, re
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from main.Database.database import Database
from .. import API_ID, API_HASH, MONGODB_URI

# ---------- login / logout ----------
async def login(uid: int, api_id: int, api_hash: str, session: str) -> None:
    db = Database(MONGODB_URI, 'saverestricted')
    await asyncio.gather(
        db.update_api_id(uid, api_id),
        db.update_api_hash(uid, api_hash),
        db.update_session(uid, session)
    )

async def logout(uid: int) -> None:
    db = Database(MONGODB_URI, 'saverestricted')
    await asyncio.gather(
        db.rem_api_id(uid),
        db.rem_api_hash(uid),
        db.rem_session(uid)
    )

# ---------- join ----------
async def join(client: Client, invite: str) -> str:
    try:
        await client.join_chat(invite)
        await asyncio.sleep(1)
        return "✅ Joined successfully."
    except FloodWait as fw:
        await asyncio.sleep(fw.value)
        return f"⏳ FloodWait {fw.value}s"
    except Exception:
        return "❌ Failed to join."

# ---------- link extractor ----------
def get_link(text: str) -> str | None:
    pattern = r"(?i)\b((?:https?://)?(?:t\.me|www\.\w+\.\w+)/[^\s]+)"
    match = re.search(pattern, text)
    return match.group(1) if match else None

# ---------- anti-spam ----------
spam_user, spam_time = [], []

async def set_timer(bot, uid: int) -> None:
    now = time.time()
    spam_user.append(uid); spam_time.append(now)
    tmp = await bot.send_message(uid, "⏳ Cool-down 23 s …")
    await asyncio.sleep(25)
    await tmp.edit("✅ You can forward again.")
    spam_user.remove(uid); spam_time.remove(now)

def check_timer(uid: int) -> tuple[bool, str | None]:
    if uid in spam_user:
        left = 24 - round(time.time() - spam_time[spam_user.index(uid)])
        return False, f"Wait {left}s"
    return True, None

# ---------- thumbnail ----------
async def screenshot(video: str, ts: int | float, uid: int) -> str | None:
    thumb = f"{uid}.jpg"
    if os.path.exists(thumb):
        return thumb
    cmd = ["ffmpeg", "-ss", str(ts), "-i", video, "-vframes", "1", thumb]
    proc = await asyncio.create_subprocess_exec(*cmd,
                                                stdout=asyncio.subprocess.PIPE,
                                                stderr=asyncio.subprocess.PIPE)
    await proc.communicate()
    return thumb if os.path.isfile(thumb) else None
