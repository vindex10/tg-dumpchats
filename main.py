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



async def main():
    client = Client(
        api_id=API_ID,
        api_hash=API_HASH,
        phone_number=PHONE_NUMBER
    )

    all_chat_names = {}
    async with client:
        first_batch = await client.api.get_chats(api.ChatListMain(), 1)
        total_count = first_batch.total_count
        logging.info(total_count)
        while True:
            try:
                await client.api.load_chats(api.ChatListMain(), 100)
            except api.errors.NotFound as e:
                break
        all_chats_req = await client.api.get_chats(api.ChatListMain(), total_count)
        all_chat_ids = all_chats_req.chat_ids

        for chat_id in all_chat_ids:
            chat_info = await client.get_chat(chat_id)
            all_chat_names[chat_id] = chat_info.title
    with open("chat_names.json", "w", encoding="utf-8") as fout:
        json.dump(all_chat_names, fout, indent=True, ensure_ascii=False)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
