import re
import time
from html import escape
from cachetools import TTLCache
from pyrogram import filters
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultPhoto,
    InlineQueryResultVideo,
)
from TEAMZYRO import app
from TEAMZYRO.unit.zyro_inline import *

all_characters_cache = TTLCache(maxsize=10000, ttl=300)
user_collection_cache = TTLCache(maxsize=10000, ttl=30)


@app.on_inline_query()
async def inlinequery(client, query: InlineQuery) -> None:
    q = query.query.strip()
    offset = int(query.offset) if query.offset else 0

    force_refresh = '!refresh' in q
    if force_refresh:
        q = q.replace('!refresh', '').strip()
        await refresh_character_caches()

    try:
        user = None
        if q.startswith('collection.'):
            parts = q.split(' ')
            user_id = parts[0].split('.')[1]
            search_terms = ' '.join(parts[1:]) if len(parts) > 1 else ''
            if user_id.isdigit():
                user = await get_user_collection(user_id)
                if user:
                    all_characters = list({
                        char['id']: char
                        for char in user.get('characters', [])
                        if 'id' in char
                    }.values())
                    if search_terms:
                        regex = re.compile(search_terms, re.IGNORECASE)
                        all_characters = [
                            char for char in all_characters
                            if (regex.search(char.get('name', '')) or
                                regex.search(char.get('anime', '')) or
                                regex.search(' '.join(char.get('aliases', []))))
                        ]
                else:
                    all_characters = []
            else:
                all_characters = []
        else:
            if q:
                all_characters = await search_characters(q, force_refresh)
            else:
                all_characters = await get_all_characters(force_refresh)

        if '.AMV' in q:
            all_characters = [c for c in all_characters if c.get('vid_url')]
        else:
            all_characters = [c for c in all_characters if c.get('img_url')]

        characters = all_characters[offset:offset + 50]
        next_offset = str(offset + len(characters)) if len(characters) == 50 else ""

        results = []
        for character in characters:
            if not all(k in character for k in ['id', 'name', 'anime', 'rarity']):
                continue

            if user:
                user_character_count = sum(
                    1 for char in user.get('characters', [])
                    if char.get('id') == character['id']
                )
                caption = (
                    f"<b>👤 Look At {escape(user.get('first_name', 'User'))}'s Collection:</b>\n"
                    f"🌸 <b>{escape(character['name'])} (x{user_character_count})</b>\n"
                    f"<b>🏖️ From: {escape(character['anime'])}</b>\n"
                    f"<b>🔮 Rarity: {escape(character['rarity'])}</b>\n"
                    f"<b>🆔 <code>{escape(str(character['id']))}</code></b>\n"
                )
            else:
                caption = (
                    f"<b>Character Details:</b>\n\n"
                    f"🌸 <b>{escape(character['name'])}</b>\n"
                    f"<b>🏖️ From: {escape(character['anime'])}</b>\n"
                    f"<b>🔮 Rarity: {escape(character['rarity'])}</b>\n"
                    f"<b>🆔 <code>{escape(str(character['id']))}</code></b>\n"
                )

            if character.get('vid_url'):
                results.append(InlineQueryResultVideo(
                    video_url=character['vid_url'],
                    mime_type="video/mp4",
                    thumb_url=character.get('thum_url', 'https://files.catbox.moe/f5njbm.jpg'),
                    title=character['name'],
                    description=f"{character['anime']} | {character['rarity']}",
                    caption=caption,
                    parse_mode="html",
                    id=f"{character['id']}_{time.time()}",
                ))
            elif character.get('img_url'):
                results.append(InlineQueryResultPhoto(
                    photo_url=character['img_url'],
                    thumb_url=character['img_url'],
                    caption=caption,
                    parse_mode="html",
                    id=f"{character['id']}_{time.time()}",
                ))

        await query.answer(results=results, next_offset=next_offset, cache_time=1)

    except Exception as e:
        print(f"Error in inlinequery: {e}")
        await query.answer(results=[], cache_time=1)
