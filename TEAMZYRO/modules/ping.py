import time
import random

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from TEAMZYRO import application, sudo_users, START_MEDIA

async def ping(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in sudo_users:
        update.message.reply_text("Nouu.. its Sudo user's Command..")
        return
    start_time = time.time()
    media = random.choice(START_MEDIA)
    
    ping_text = "<blockquote>❛ ᴘɪɴɢ ᴘᴏɴɢ .... 💗</blockquote>"

    try:
        if media.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            message = await update.message.reply_photo(
                photo=media,
                caption=ping_text,
                parse_mode="HTML"
            )
        else:
            message = await update.message.reply_video(
                video=media,
                caption=ping_text,
                parse_mode="HTML"
            )
    except:
        message = await update.message.reply_text(ping_text, parse_mode="HTML")
    
    end_time = time.time()
    elapsed_time = round((end_time - start_time) * 1000, 3)
    
    updated_text = f"<blockquote>❛ ᴘɪɴɢ ᴘᴏɴɢ .... 💗\n\n⚡ Pong! {elapsed_time}ms</blockquote>"
    try:
        await message.edit_caption(caption=updated_text, parse_mode="HTML")
    except:
        await message.edit_text(updated_text, parse_mode="HTML")

application.add_handler(CommandHandler("ping", ping))
