import json
from asyncio import Future
from collections import Counter
from dataclasses import dataclass, field

import datetime as datetime
from typing import List, Union, Coroutine, Any

import telethon
from telethon import TelegramClient
from telethon.hints import Entity
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetID

with open("config.json", "r") as f:
    conf = json.load(f)
    api_id = conf["api_id"]
    api_hash = conf["api_hash"]
    chat_id = conf["chat_id"]


set_cache = {}


@dataclass
class StickerSet:
    set_id: int
    access_hash: int
    title: str
    handle: str
    set_result: Any = field(compare=False)

    def __eq__(self, other):
        return isinstance(other, StickerSet) and self.set_id == other.set_id

    def __hash__(self):
        return hash((self.__class__, self.set_id))

    def __str__(self):
        return self.title


@dataclass
class Sticker:
    message_id: int
    datetime: datetime
    emoji: str
    sticker_id: int
    set: StickerSet
    document: Any

    def __eq__(self, other):
        return isinstance(other, Sticker) and self.sticker_id == other.sticker_id

    def __hash__(self):
        return hash((self.__class__, self.sticker_id))


async def scrape_chat(c: TelegramClient, chat: Entity) -> List[Sticker]:
    sticker_list = []
    async for m in c.iter_messages(chat):
        if not m.sticker:
            continue
        set_data = m.sticker.attributes[1].stickerset
        sticker_set = await get_sticker_set(c, set_data.id, set_data.access_hash)
        sticker = Sticker(
            m.id,
            m.date,
            m.sticker.attributes[1].alt,
            m.sticker.id,
            sticker_set,
            m.document
        )
        sticker_list.append(sticker)
        print(sticker)
    return sticker_list


async def get_sticker_set(c: TelegramClient, set_id: int, set_hash: int) -> StickerSet:
    if set_id in set_cache:
        return set_cache[set_id]
    result = await c(GetStickerSetRequest(InputStickerSetID(set_id, set_hash)))
    set_cache[set_id] = StickerSet(
        result.set.id,
        result.set.access_hash,
        result.set.title,
        result.set.short_name,
        result
    )
    return set_cache[set_id]


async def send_sticker(c: TelegramClient, chat: Entity, sticker: Sticker) -> None:
    sticker_set = sticker.set.set_result
    sticker_doc = None
    for sticker_file in sticker_set.documents:
        if sticker_file.id == sticker.sticker_id:
            sticker_doc = sticker_file
            break
    await c.send_file(chat, sticker_doc)


def generate_stats_messages(sticker_list: List[Sticker]) -> List[str]:
    emoji_list = []
    sticker_id_list = []
    set_list = []
    for sticker in sticker_list:
        emoji_list.extend(sticker.emoji.split())
        sticker_id_list.append(sticker.sticker_id)
        set_list.append(sticker.set)
    emoji = Counter(emoji_list)
    sticker_ids = Counter(sticker_id_list)
    sticker_set_ids = Counter(set_list)
    sticker_set_str = "Counter(" + ', '.join(f"\"{sset}\": {n}" for sset, n in sticker_set_ids.most_common()) + ")"
    return [
        f"Emoji counter: {emoji}",
        f"Sticker ID counter: {sticker_ids}",
        f"Set counter: {sticker_set_str}"
    ]


async def send_top_stickers(c: TelegramClient, chat: Entity, sticker_list: List[Sticker], count: int) -> None:
    counter = Counter(sticker_list)
    position = 1
    for sticker, n in counter.most_common(count):
        await c.send_message(chat, f"Sticker #{position}, used on {n} days:")
        await c.send_file(chat, sticker.document)
        position += 1


def sync(c: TelegramClient, future: Union[Future, Coroutine]) -> Any:
    return c.loop.run_until_complete(future)


if __name__ == '__main__':
    client = telethon.TelegramClient('sticker_counter', api_id, api_hash)
    client.start()
    sticker_chat = sync(client, client.get_entity(chat_id))
    stickers = sync(client, scrape_chat(client, sticker_chat))
    stats_msgs = generate_stats_messages(stickers)
    for stats_msg in stats_msgs:
        sync(client, client.send_message(sticker_chat, stats_msg))
    sync(client, send_top_stickers(client, "me", stickers, 5))
