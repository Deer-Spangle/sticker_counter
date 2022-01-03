from datetime import datetime
from time import sleep
from typing import List

import telethon
from prometheus_client import start_http_server, Gauge, Counter
from telethon import TelegramClient
from telethon.hints import Entity
from telethon.tl.functions.messages import GetRecentStickersRequest

from sticker_counter import Sticker
from stickers import get_sticker_set, RecentSticker
from util import api_id, api_hash, sync, chat_id, prom_port


sticker_count = Counter(
    "stickercounter_logger_sticker_total",
    "Total count of stickers logged",
    labelnames=["emoji"]
)
sticker_count.labels(emoji="🤗")
latest_sticker = Gauge("stickercounter_logger_latest_sticker_unixtime", "Last time a sticker was logged")
start_time = Gauge("stickercounter_logger_startup_unixtime", "Last time the sticker logger was started")


async def list_recent_stickers(c: TelegramClient) -> List[RecentSticker]:
    result = await c(GetRecentStickersRequest(hash=0))
    recent = []
    for use_date, sticker in zip(result.dates, result.stickers):
        recent.append(
            RecentSticker(
                datetime.utcfromtimestamp(use_date),
                Sticker(
                    sticker.attributes[1].alt,
                    sticker.id,
                    await get_sticker_set(
                        c,
                        sticker.attributes[1].stickerset.id,
                        sticker.attributes[1].stickerset.access_hash
                    ),
                    sticker
                )
            )
        )
    return recent


async def check_new_sticker_usage(
        c: TelegramClient,
        old_recent: List[RecentSticker],
        log_chat: Entity
) -> List[RecentSticker]:
    new_recent = await list_recent_stickers(c)
    for new in new_recent:
        if new not in old_recent:
            print(f"Posting new sticker: {new.sticker.emoji} {new.sticker.sticker_id}")
            sticker_count.labels(emoji=new.sticker.emoji).inc()
            latest_sticker.set_to_current_time()
            await c.send_file(log_chat, new.sticker.document)
        else:
            break
    new_recent = await list_recent_stickers(c)
    return new_recent

if __name__ == '__main__':
    client = telethon.TelegramClient('sticker_counter', api_id, api_hash)
    client.start()
    recent_stickers = sync(client, list_recent_stickers(client))
    chat = sync(client, client.get_entity(chat_id))
    start_http_server(prom_port)
    start_time.set_to_current_time()
    print("Startup complete")
    while True:
        recent_stickers = sync(client, check_new_sticker_usage(client, recent_stickers, chat))
        print("Waiting for more...")
        sleep(60)
