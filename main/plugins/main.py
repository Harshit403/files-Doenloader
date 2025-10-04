# main.py

import os, time, asyncio, re, cv2
from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, BadRequest, ChannelPrivate, UsernameInvalid, PeerIdInvalid, ChatAdminRequired

from .. import bot, API_ID, API_HASH, BOT_TOKEN, FORCESUB, Bot
from ..plugins.helpers import get_link, join, set_timer, check_timer, check_private_channel_access
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
    is_private = False

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
            await edit.edit('❌ Unsupported link format.')
            return
    except (ValueError, IndexError):
        await edit.edit('❌ Invalid message link format.')
        return

    # Pre-check for private channel access
    if is_private:
        await edit.edit('🔍 Checking access to private channel/group...')
        if not await check_private_channel_access(userbot, chat_id):
            await edit.edit(
                f'❌ Access Denied to Channel ID: `{chat_id}`\n\n'
                'Your user account cannot access this private channel/group.\n\n'
                '**Solutions:**\n'
                '1. Join the channel/group with this user account.\n'
                '2. If already a member, try leaving and re-joining.\n'
                '3. The channel may have restrictions on content access.'
            )
            return

    try:
        msg = await userbot.get_messages(chat_id, msg_id)
    except PeerIdInvalid:
        # This can happen if the check above passes but get_messages still fails
        await edit.edit(
            f'❌ Peer ID Invalid: `{chat_id}`\n\n'
            'Could not fetch the message. This is a strict access error.\n'
            'Ensure your user account is a member and not restricted.'
        )
        return
    except (ChannelPrivate, UsernameInvalid, BadRequest) as e:
        await edit.edit(f'❌ Cannot access message: `{e}`')
        return
    except Exception as e:
        await edit.edit(f'❌ Failed to fetch message: `{e}`')
        return

    if not msg.media and not msg.text and not msg.caption:
        await edit.edit('⚠️ Message has no forwardable content.')
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
        except Exception as e:
            # If direct copy fails, we will fall back to download
            await edit.edit(f'⚠️ Direct copy failed, trying download method... Error: {e}')

    # --- Fallback: download + re-upload ---
    file = None
    thumb_path = None
    try:
        await edit.edit('📥 Downloading media...')
        file = await userbot.download_media(
            msg,
            progress=progress_for_pyrogram,
            progress_args=(userbot, '📥 Downloading…', edit, time.time())
        )
        if not file:
            await edit.edit('❌ Failed to download media. The file might be inaccessible or deleted.')
            return

        caption = msg.caption or ''
        entities = msg.caption_entities
        await edit.edit('📤 Uploading…')

        if msg.video_note:
            meta = video_meta(file)
            thumb_path = await gen_thumb(file, f'{sender}.jpg')
            await client.send_video_note(
                sender, file, length=meta['height'], duration=meta['duration'],
                thumb=thumb_path, progress=progress_for_pyrogram,
                progress_args=(client, '📤 Uploading…', edit, time.time())
            )
        elif msg.video:
            meta = video_meta(file)
            thumb_path = await gen_thumb(file, f'{sender}.jpg')
            await client.send_video(
                sender, file, caption=caption, caption_entities=entities,
                duration=meta['duration'], width=meta['width'], height=meta['height'],
                thumb=thumb_path, progress=progress_for_pyrogram,
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

        me = await client.get_me()
        await edit.edit(f'✅ Forwarded to @{me.username}.')

    except PeerIdInvalid:
        # This is the most likely place for the error to occur during download
        await edit.edit(
            f'❌ Download Failed: Peer ID Invalid `{chat_id}`\n\n'
            'Your account can see the channel but is restricted from downloading media.\n'
            'This is a channel-specific setting that cannot be bypassed.'
        )
    except FloodWait as fw:
        await asyncio.sleep(fw.value)
        await edit.edit(f'⚠️ FloodWait: Retry after {fw.value} seconds.')
    except Exception as e:
        await edit.edit(f'❌ An error occurred during processing: `{e}`')
    finally:
        # --- Clean up temporary files ---
        if file and os.path.isfile(file):
            os.remove(file)
        if thumb_path and os.path.isfile(thumb_path):
            os.remove(thumb_path)


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
            # This is the final catch-all, should not be reached if get_msg handles everything
            await init.edit(f'💥 Unexpected critical error: {e}')

    await userbot.stop()
    await jvbot.stop()
