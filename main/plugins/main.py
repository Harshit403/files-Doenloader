import os, time, asyncio, re, cv2
from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, BadRequest, ChannelPrivate, UsernameInvalid, PeerIdInvalid

from .. import bot, API_ID, API_HASH, BOT_TOKEN, FORCESUB, Bot
from ..plugins.helpers import get_link, join, set_timer, check_timer
from ..plugins.display_progress import progress_for_pyrogram
from ..Database.database import Database
from main.plugins.dbstuff import db

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.WARNING)

process = []
timer = []

async def is_user_subscribed(uid):
    if not FORCESUB:
        return True
    try:
        await bot.get_chat_member(FORCESUB, uid)
        return True
    except:
        return False

def video_meta(path):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        return dict(duration=0, width=0, height=0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = int(frames / fps) if fps else 0
    cap.release()
    return dict(duration=duration, width=width, height=height)

async def gen_thumb(video, out):
    cap = cv2.VideoCapture(video)
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) // 2))
    ret, frame = cap.read()
    cap.release()
    if ret:
        cv2.imwrite(out, frame)
        return out
    return None

async def get_msg(userbot, client, sender, msg_link, edit):
    chat_id = None
    msg_id = None

    try:
        if 't.me/c/' in msg_link:
            chat_id = int('-100' + msg_link.split('/')[-2])
            msg_id = int(msg_link.split('/')[-1].split('?')[0])
            is_private = True
        elif 't.me/b/' in msg_link:
            chat_id = int(msg_link.split('/')[-2])
            msg_id = int(msg_link.split('/')[-1].split('?')[0])
            is_private = True
        elif 't.me/' in msg_link:
            username = msg_link.split('/')[-2]
            msg_id = int(msg_link.split('/')[-1].split('?')[0])
            chat_id = username
            is_private = False
        else:
            await edit.edit('❌ Unsupported link.')
            return
    except (ValueError, IndexError):
        await edit.edit('❌ Invalid message link.')
        return

    try:
        msg = await userbot.get_messages(chat_id, msg_id)
    except (ChannelPrivate, UsernameInvalid, PeerIdInvalid, BadRequest) as e:
        await edit.edit(f'❌ Cannot access message: {e}')
        return
    except Exception as e:
        await edit.edit(f'❌ Failed to fetch message: {e}')
        return

    if not msg.media and not msg.text and not msg.caption:
        await edit.edit('⚠️ Message has no content.')
        return

    # Try direct copy for public chats
    if not is_private:
        try:
            if msg.media_group_id:
                await client.copy_media_group(sender, msg.chat.id, msg.id)
            else:
                await client.copy_message(sender, msg.chat.id, msg.id)
            me = await client.get_me()
            await edit.edit(f'✅ Forwarded to @{me.username}.')
            return
        except (ChannelPrivate, BadRequest, PeerIdInvalid):
            pass  # fallback to download
        except Exception as e:
            await edit.edit(f'⚠️ Copy failed, falling back to download: {e}')

    # Fallback: download + re-upload
    file = await userbot.download_media(
        msg,
        progress=progress_for_pyrogram,
        progress_args=(userbot, '📥 Downloading…', edit, time.time())
    )
    if not file:
        await edit.edit('❌ Failed to download media.')
        return

    caption = msg.caption or ''
    entities = msg.caption_entities
    await edit.edit('📤 Uploading…')

    try:
        if msg.video_note:
            meta = video_meta(file)
            thumb = await gen_thumb(file, f'{sender}.jpg')
            await client.send_video_note(
                sender, file, length=meta['height'], duration=meta['duration'],
                thumb=thumb, progress=progress_for_pyrogram,
                progress_args=(client, '📤 Uploading…', edit, time.time())
            )
        elif msg.video:
            meta = video_meta(file)
            thumb = await gen_thumb(file, f'{sender}.jpg')
            await client.send_video(
                sender, file, caption=caption, caption_entities=entities,
                duration=meta['duration'], width=meta['width'], height=meta['height'],
                thumb=thumb, progress=progress_for_pyrogram,
                progress_args=(client, '📤 Uploading…', edit, time.time())
            )
        elif msg.photo:
            await client.send_photo(sender, file, caption=caption, caption_entities=entities)
        elif msg.audio:
            await client.send_audio(sender, file, caption=caption, caption_entities=entities,
                                    progress=progress_for_pyrogram,
                                    progress_args=(client, '📤 Uploading…', edit, time.time()))
        else:
            await client.send_document(sender, file, caption=caption, caption_entities=entities,
                                       progress=progress_for_pyrogram,
                                       progress_args=(client, '📤 Uploading…', edit, time.time()))
    except FloodWait as fw:
        await asyncio.sleep(fw.value)
        await edit.edit(f'⚠️ FloodWait: Retry after {fw.value} seconds.')
    except Exception as e:
        await edit.edit(f'❌ Upload failed: {e}')
    else:
        me = await client.get_me()
        await edit.edit(f'✅ Forwarded to @{me.username}.')

    if os.path.isfile(file):
        os.remove(file)
    if os.path.isfile(f'{sender}.jpg'):
        os.remove(f'{sender}.jpg')

@Bot.on_message(filters.private & filters.incoming)
async def clone_handler(bot_, event: Message):
    link = get_link(event.text)
    if not link:
        return

    init = await event.reply('⏳ Processing...')
    if not await is_user_subscribed(event.from_user.id):
        return await init.edit(
            '🔒 Join the channel first.',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('Join Channel', url=f'https://t.me/{FORCESUB}')]
            ])
        )

    bot_token = await db.get_botCreds(event.from_user.id)
    if not bot_token:
        return await init.edit('🤖 Connect your bot via /connect.')

    jvbot = Client(
        name=str(event.from_user.id),
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=bot_token,
        in_memory=True
    )
    try:
        await jvbot.start()
    except Exception as e:
        return await init.edit(f'❌ Bot token error: {e}')

    creds = await db.get_credentials(event.from_user.id)
    if not creds or not all(creds):
        await jvbot.stop()
        return await init.edit('🔑 Login first via /login or /session.')

    userbot = Client(
        name='user',
        api_id=creds[0],
        api_hash=creds[1],
        session_string=creds[2],
        in_memory=True
    )
    try:
        await userbot.start()
    except Exception as e:
        await jvbot.stop()
        return await init.edit(f'❌ User session error: {e}')

    if 't.me/+' in link or 't.me/joinchat/' in link:
        out = await join(userbot, link)
        await init.edit(out)
    else:
        try:
            await get_msg(userbot, jvbot, event.from_user.id, link, init)
        except FloodWait as fw:
            await asyncio.sleep(fw.value)
            await init.edit(f'⏳ Retry after {fw.value} seconds.')
        except Exception as e:
            await init.edit(f'💥 Unexpected error: {e}')

    await userbot.stop()
    await jvbot.stop()
