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

CHANNEL_ID = config["channel_id"]


async def write_out(QUEUE):
    with open("out.dat", "w", encoding="utf-8") as fout:
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
        while last_id is not None:
            batch = await client.api.get_chat_history(chat_id=CHANNEL_ID, from_message_id=last_id,
                                                      offset=0, limit=10, only_local=False)
            m = None
            logging.info("%s / %s", len(batch.messages), total)
            for m in batch.messages:
                if not isinstance(m.content, api.types.MessageText):
                    continue
                await QUEUE.put({
                    "id": m.id,
                    "text": str(m.content.text.text)
                })
            total += len(batch.messages)
            last_id = m.id if m is not None else None
        logging.info("push None")
        await QUEUE.put(None)
    logging.info("DONE reading")


async def themain():
    QUEUE = asyncio.Queue()
    await asyncio.gather(write_out(QUEUE), main(QUEUE))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(themain())
