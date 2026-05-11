from TEAMZYRO import *
import random
import asyncio

log = "-1002792716047"

RARITY_WEIGHTS = {
    "⚪️ Low": (40, True),
    "🟠 Medium": (20, True),
    "🔴 High": (12, True),
    "🎩 Special Edition": (8, True),
    "🪽 Elite Edition": (6, True),
    "🪐 Exclusive": (4, True),
    "💞 Valentine": (2, False),
    "🎃 Halloween": (2, False),
    "❄️ Winter": (1.5, False),
    "🏖 Summer": (1.2, False),
    "🎗 Royal": (0.5, False),
    "💸 Luxury Edition": (0.5, False)
}


async def delete_message(chat_id, message_id):
    await asyncio.sleep(300)
    try:
        await app.delete_messages(chat_id, message_id)
    except Exception as e:
        print(f"Error deleting message: {e}")


async def send_image(message, _context=None) -> None:
    chat_id = message.chat.id

    all_characters = await collection.find(
        {"rarity": {"$in": [k for k, v in RARITY_WEIGHTS.items() if v[1]]}}
    ).to_list(length=None)

    if not all_characters:
        await app.send_message(chat_id, "No characters found with allowed rarities in the database.")
        return

    available_characters = [
        c for c in all_characters
        if 'id' in c and c.get('rarity') is not None and RARITY_WEIGHTS.get(c['rarity'], (0, False))[1]
    ]

    if not available_characters:
        await app.send_message(chat_id, "No available characters with the allowed rarities.")
        return

    cumulative_weights = []
    cumulative_weight = 0
    for character in available_characters:
        cumulative_weight += RARITY_WEIGHTS.get(character.get('rarity'), (1, False))[0]
        cumulative_weights.append(cumulative_weight)

    rand = random.uniform(0, cumulative_weight)
    selected_character = None
    for i, character in enumerate(available_characters):
        if rand <= cumulative_weights[i]:
            selected_character = character
            break

    if not selected_character:
        selected_character = random.choice(available_characters)

    last_characters[chat_id] = selected_character
    last_characters[chat_id]['timestamp'] = time.time()

    if chat_id in first_correct_guesses:
        del first_correct_guesses[chat_id]

    caption_text = (
        f"✨ A {selected_character['rarity']} Character Appears! ✨\n"
        "🔍 Use /guess to claim this mysterious character!\n"
        "💫 Hurry, before someone else snatches them!"
    )

    if 'vid_url' in selected_character:
        sent_message = await app.send_video(
            chat_id=chat_id,
            video=selected_character['vid_url'],
            caption=caption_text,
        )
    else:
        sent_message = await app.send_photo(
            chat_id=chat_id,
            photo=selected_character['img_url'],
            caption=caption_text,
        )

    asyncio.create_task(delete_message(chat_id, sent_message.id))
