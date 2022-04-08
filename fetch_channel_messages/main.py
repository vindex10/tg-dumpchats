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

CHANNEL_ID = None


async def write_out(QUEUE):
    with open(f"chat_{CHANNEL_ID}.dat", "w", encoding="utf-8") as fout:
        while True:
            elem = await QUEUE.get()
            if elem is None:
                logging.info("writer got None")
                break
            line = json.dumps(elem, ensure_ascii=False)
            fout.write(f"{line}\n")
    logging.info("DONE writing")


async def main(QUEUE):
    client = Client(
        api_id=API_ID,
        api_hash=API_HASH,
        phone_number=PHONE_NUMBER
    )

    async with client:
        last_id = 0
        total = 0
        fetched = 0
        while fetched < 7000:
            batch = await client.api.get_chat_history(chat_id=CHANNEL_ID, from_message_id=last_id,
                                                      offset=0, limit=100, only_local=False,
                                                      request_timeout=1000)
            m = None
            logging.info("%s : %s / %s", len(batch.messages), fetched, total)
            for m in batch.messages:
                if not isinstance(m.content, api.types.MessageText):
                    continue
                fetched += 1
                await QUEUE.put({
                    "id": m.id,
                    "text": str(m.content.text.text)
                })
            total += len(batch.messages)
            if m is None:
                await asyncio.sleep(5)
                continue
            last_id = m.id
            await asyncio.sleep(0.3)
        logging.info("push None")
        await QUEUE.put(None)
    logging.info("DONE reading")


async def themain():
    QUEUE = asyncio.Queue()
    await asyncio.gather(write_out(QUEUE), main(QUEUE))


if __name__ == '__main__':
    CHANNEL_ID = int(sys.argv[1])
    logging.basicConfig(level=logging.INFO)
    asyncio.run(themain())
