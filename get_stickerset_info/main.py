import sys
import logging
import asyncio
import json

from aiotdlib import Client
from aiotdlib.api import API
from aiotdlib import api

with open("config.json", "r", encoding="utf-8") as fin:
    config = json.load(fin)

API_ID = config["api_id"]
API_HASH = config["api_hash"]
PHONE_NUMBER = config["phone_number"]
STICKER_SET_ID = None


async def main():
    client = Client(
        api_id=API_ID,
        api_hash=API_HASH,
        phone_number=PHONE_NUMBER
    )

    async with client:
        res = await client.api.get_sticker_set(STICKER_SET_ID)
    with open(f"stickerset-{STICKER_SET_ID}.json", "w", encoding="utf-8") as fout:
        json.dump(json.loads(res.json()), fout, ensure_ascii=False, indent=True)

if __name__ == '__main__':
    STICKER_SET_ID = int(sys.argv[1])
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
