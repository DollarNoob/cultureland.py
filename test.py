import cultureland
import os
import mTranskey
import mTranskey.transkey
import httpx
import asyncio
from dotenv import load_dotenv
from pin import Pin

load_dotenv()

async def main():
    client = cultureland.Cultureland()
    print("Login:", await client.login(os.getenv("CULTURELAND_KEEP_LOGIN_INFO")))
    print("is currently logged in:", await client.is_login())
    balance = await client.get_balance()
    print("balance:", balance.__dict__)
    print("charge:", await client.charge(Pin("3110-1234-1234-5678")))

asyncio.run(main())
