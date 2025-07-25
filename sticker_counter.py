from collections import Counter

from typing import List, Callable

import telethon
from telethon import TelegramClient
from telethon.hints import Entity

from stickers import Sticker, get_sticker_set, StickerMessage
from util import sync, api_id, api_hash, chat_id, my_sticker_set_substring, chunks


async def scrape_chat(c: TelegramClient, chat: Entity) -> List[StickerMessage]:
    sticker_list = []
    async for m in c.iter_messages(chat):
        if not m.sticker:
            continue
        set_data = m.sticker.attributes[1].stickerset
        sticker_set = await get_sticker_set(c, set_data.id, set_data.access_hash)
        sticker = StickerMessage(
            m.id,
            m.date,
            Sticker(
                m.sticker.attributes[1].alt,
                m.sticker.id,
                sticker_set,
                m.document
            )
        )
        sticker_list.append(sticker)
        print(sticker)
    return sticker_list


async def send_sticker(c: TelegramClient, chat: Entity, sticker: Sticker) -> None:
    sticker_set = sticker.set.set_result
    sticker_doc = None
    for sticker_file in sticker_set.documents:
        if sticker_file.id == sticker.sticker_id:
            sticker_doc = sticker_file
            break
    await c.send_file(chat, sticker_doc)


def generate_stats_messages(sticker_list: List[StickerMessage]) -> List[str]:
    emoji_list = []
    sticker_id_list = []
    set_list = []
    for sticker in sticker_list:
        emoji_list.extend(sticker.sticker.emoji.split())
        sticker_id_list.append(sticker.sticker.sticker_id)
        set_list.append(sticker.sticker.set)
    emoji = Counter(emoji_list)
    sticker_ids = Counter(sticker_id_list)
    sticker_set_ids = Counter(set_list)
    sticker_set_str = "Counter(" + ', '.join(f"\"{sset}\": {n}" for sset, n in sticker_set_ids.most_common()) + ")"
    return [
        f"Emoji counter: {emoji}",
        f"Sticker ID counter: {sticker_ids}",
        f"Set counter: {sticker_set_str}"
    ]


async def send_top_stickers(
        c: TelegramClient,
        chat: Entity,
        sticker_list: List[StickerMessage],
        count: int,
        sticker_filter: Callable[[StickerMessage], bool] = None
) -> None:
    if sticker_filter is None:
        sticker_filter = lambda x: True
    counter = Counter([msg.sticker for msg in sticker_list if sticker_filter(msg)])
    position = 1
    for sticker, n in counter.most_common(count):
        await c.send_message(chat, f"Sticker #{position}, used on {n} days:")
        await c.send_file(chat, sticker.document)
        position += 1



if __name__ == '__main__':
    client = telethon.TelegramClient('sticker_counter', api_id, api_hash)
    client.start()
    sticker_chat = sync(client, client.get_entity(chat_id))
    stickers = sync(client, scrape_chat(client, sticker_chat))
    stats_msgs = generate_stats_messages(stickers)
    for stats_msg in stats_msgs:
        for chunk in chunks(stats_msg, 4000):
            sync(client, client.send_message(sticker_chat, chunk))
    sync(client, client.send_message("me", "Overall top 5 stickers used"))
    sync(client, send_top_stickers(client, "me", stickers, 5))
    if my_sticker_set_substring is not None:
        sync(client, client.send_message("me", "Top 5 of my stickers used"))
        my_stickers_filter = lambda smsg: smsg.sticker.set.title is not None and my_sticker_set_substring.lower() in smsg.sticker.set.title.lower()
        sync(client, send_top_stickers(client, "me", stickers, 5, my_stickers_filter))

