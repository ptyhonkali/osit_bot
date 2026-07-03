import asyncio
from telethon import TelegramClient

API_ID=31906810
API_HASH="f568031e738ef0c55d4002298f78d74b"

client = TelegramClient("sessions/osint", API_ID, API_HASH)

async def main():
    await client.start()

    me = await client.get_me()
    print(me)

asyncio.run(main())
