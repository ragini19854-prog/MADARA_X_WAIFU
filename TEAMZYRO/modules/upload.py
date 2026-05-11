import os
import base64
import requests
import asyncio
from pyrogram import filters
from TEAMZYRO import (
    application,
    CHARA_CHANNEL_ID,
    SUPPORT_CHAT,
    OWNER_ID,
    collection,
    user_collection,
    db,
    SUDO,
    rarity_map,
    ZYRO,
    require_power
)

IMGBB_API_KEY = "62736b1fc27c5c6bb91063f2ec92913b"

WRONG_FORMAT_TEXT = """Wrong ❌ format...  eg. /upload reply to photo muzan-kibutsuji Demon-slayer 3

format:- /upload reply character-name anime-name rarity-number

use rarity number accordingly rarity Map

rarity_map = {
    1: "⚪️ Low",
    2: "🟠 Medium",
    3: "🔴 High",
    4: "🎩 Special Edition",
    5: "🪽 Elite Edition",
    6: "🪐 Exclusive",
    7: "💞 Valentine",
    8: "🎃 Halloween",
    9: "❄️ Winter",
    10: "🏖 Summer",
    11: "🎗 Royal",
    12: "💸 Luxury Edition",
    13: "🍃 echhi",
    14: "🌧️ Rainy Edition",
    15: "🎍 Festival"
}
"""

async def find_available_id():
    cursor = collection.find().sort("id", 1)
    ids = []
    async for doc in cursor:
        if "id" in doc:
            try:
                ids.append(int(doc["id"]))
            except Exception:
                continue
    ids.sort()
    for i in range(1, len(ids) + 2):
        if i not in ids:
            return str(i).zfill(2)
    return str(len(ids) + 1).zfill(2)

def upload_to_imgbb(file_path):
    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError("file_path is missing or file does not exist")

    with open(file_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    response = requests.post(
        "https://api.imgbb.com/1/upload",
        data={
            "key": IMGBB_API_KEY,
            "image": image_data,
        },
        timeout=60
    )

    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            return result["data"]["url"]
        else:
            raise Exception(f"ImgBB upload failed: {result}")
    else:
        raise Exception(f"Error uploading to ImgBB: {response.status_code} {response.text}")

upload_lock = asyncio.Lock()

@ZYRO.on_message(filters.command(["upload"]))
@require_power("add_character")
async def ul(client, message):
    global upload_lock

    if upload_lock.locked():
        return await message.reply_text("Another upload is in progress. Please wait until it is completed.")

    async with upload_lock:
        reply = message.reply_to_message
        if not reply:
            return await message.reply_text("Please reply to a photo, document, or video with the /upload command.")

        args = message.text.strip().split()
        if len(args) != 4:
            return await client.send_message(chat_id=message.chat.id, text=WRONG_FORMAT_TEXT)

        try:
            character_name = args[1].replace('-', ' ').title()
            anime = args[2].replace('-', ' ').title()
            rarity = int(args[3])
        except Exception:
            return await message.reply_text("Invalid command format. Check /upload usage.")

        if rarity not in rarity_map:
            return await message.reply_text("Invalid rarity value. Please use a valid one from the rarity map.")

        rarity_text = rarity_map[rarity]
        available_id = await find_available_id()

        character = {
            'name': character_name,
            'anime': anime,
            'rarity': rarity_text,
            'rarity_number': rarity,
            'id': available_id
        }

        processing_message = await message.reply_text("ᴜᴘʟᴏᴀᴅɪɴɢ....")
        path = None
        thumb_path = None
        try:
            path = await reply.download()
            if not path or not os.path.exists(path):
                raise Exception("Failed to download media.")

            imgbb_url = upload_to_imgbb(path)

            if reply.photo or reply.document:
                character['img_url'] = imgbb_url
            elif reply.video:
                character['vid_url'] = imgbb_url
                try:
                    thumbs = getattr(reply.video, "thumbs", None)
                    if thumbs and len(thumbs) > 0:
                        thumb_path = await client.download_media(thumbs[0].file_id)
                        if thumb_path and os.path.exists(thumb_path):
                            thumbnail_url = upload_to_imgbb(thumb_path)
                            character['thum_url'] = thumbnail_url
                except Exception:
                    pass

            caption_text = (
                f"Character Name: {character_name}\n"
                f"Anime Name: {anime}\n"
                f"Rarity: {rarity_text}\n"
                f"ID: {available_id}\n"
                f"Added by [{message.from_user.first_name}](tg://user?id={message.from_user.id})"
            )

            if 'img_url' in character:
                await client.send_photo(chat_id=CHARA_CHANNEL_ID, photo=character['img_url'], caption=caption_text)
            elif 'vid_url' in character:
                await client.send_video(chat_id=CHARA_CHANNEL_ID, video=character['vid_url'], caption=caption_text)
            else:
                await client.send_document(chat_id=CHARA_CHANNEL_ID, document=path, caption=caption_text)

            await collection.insert_one(character)

            await message.reply_text(
                f"➲ ᴀᴅᴅᴇᴅ ʙʏ» [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n"
                f"➥ Character ID: {available_id}\n"
                f"➥ Rarity: {rarity_text}\n"
                f"➥ Character Name: {character_name}"
            )
        except Exception as e:
            await message.reply_text(f"Character Upload Unsuccessful. Error: {str(e)}")
        finally:
            try:
                if path and os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass
            try:
                if thumb_path and os.path.exists(thumb_path):
                    os.remove(thumb_path)
            except Exception:
                pass
            try:
                await processing_message.delete()
            except Exception:
                pass
