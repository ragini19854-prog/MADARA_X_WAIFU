import time
import random
from pyrogram import filters
from pyrogram.types import Message
from TEAMZYRO import app, sudo_users, START_MEDIA


@app.on_message(filters.command("ping"))
async def ping(client, message: Message) -> None:
    if message.from_user.id not in sudo_users:
        await message.reply_text("Nouu.. its Sudo user's Command..")
        return

    start_time = time.time()
    media = random.choice(START_MEDIA)

    ping_text = "> ❛ ᴘɪɴɢ ᴘᴏɴɢ .... 💗"

    try:
        if media.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            sent = await message.reply_photo(photo=media, caption=ping_text)
        else:
            sent = await message.reply_video(video=media, caption=ping_text)
    except Exception:
        sent = await message.reply_text(ping_text)

    elapsed_time = round((time.time() - start_time) * 1000, 3)
    updated_text = f"> ❛ ᴘɪɴɢ ᴘᴏɴɢ .... 💗\n> \n> ⚡ Pong! {elapsed_time}ms"

    try:
        await sent.edit_caption(caption=updated_text)
    except Exception:
        await sent.edit_text(updated_text)
