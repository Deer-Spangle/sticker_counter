import json
from asyncio import Future
from typing import Any, Union, Coroutine

from telethon import TelegramClient

with open("config.json", "r") as f:
    conf = json.load(f)
    api_id = conf["api_id"]
    api_hash = conf["api_hash"]
    chat_id = conf["chat_id"]
    prom_port = conf.get("prometheus_port", 8367)
    prom_emoji = conf.get("prometheus_init_emoji", ["🤗"])
    my_sticker_set_substring = conf.get("my_sticker_set_substring", None)


def sync(c: TelegramClient, future: Union[Future, Coroutine]) -> Any:
    return c.loop.run_until_complete(future)

def chunks(input_str: str, length: int) -> list[str]:
    return [input_str[i:i+length] for i in range(0, len(input_str), length)]
