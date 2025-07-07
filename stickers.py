from dataclasses import dataclass, field
from typing import Any, Optional

import datetime as datetime
from telethon import TelegramClient
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetID
from telethon.errors.rpcerrorlist import StickersetInvalidError

set_cache = {}


@dataclass
class StickerSet:
    set_id: int
    access_hash: int
    title: Optional[str]
    handle: Optional[str]
    set_result: Any = field(compare=False)
    deleted: bool = False

    def __eq__(self, other):
        return isinstance(other, StickerSet) and self.set_id == other.set_id

    def __hash__(self):
        return hash((self.__class__, self.set_id))

    def __str__(self):
        if self.deleted:
            return f"DELETED: {self.set_id}"
        return self.title


@dataclass
class Sticker:
    emoji: str
    sticker_id: int
    set: StickerSet
    document: Any

    def __eq__(self, other):
        return isinstance(other, Sticker) and self.sticker_id == other.sticker_id

    def __hash__(self):
        return hash((self.__class__, self.sticker_id))


@dataclass
class StickerMessage:
    message_id: int
    datetime: datetime
    sticker: Sticker


@dataclass
class RecentSticker:
    datetime: datetime
    sticker: Sticker

    def __eq__(self, other):
        return isinstance(other, RecentSticker) and self.datetime == other.datetime and self.sticker == other.sticker

    def __hash__(self):
        return hash((self.__class__, self.datetime, self.sticker))


async def get_sticker_set(c: TelegramClient, set_id: int, set_hash: int) -> StickerSet:
    if set_id in set_cache:
        return set_cache[set_id]
    try:
        result = await c(GetStickerSetRequest(InputStickerSetID(set_id, set_hash), hash=0))
    except StickersetInvalidError:
        set_cache[set_id] = StickerSet(
            set_id,
            set_hash,
            None,
            None,
            None,
            True
        )
        return set_cache[set_id]
    set_cache[set_id] = StickerSet(
        result.set.id,
        result.set.access_hash,
        result.set.title,
        result.set.short_name,
        result
    )
    return set_cache[set_id]
