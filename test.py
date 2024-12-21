import cultureland
import os
import mTranskey
import mTranskey.transkey
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def main():
    client = cultureland.Cultureland()
    print("Login:", await client.login(os.getenv("CULTURELAND_KEEP_LOGIN_INFO")))
    print("is currently logged in:", await client.is_login())
    balance = await client.get_balance()
    print("balance:", balance.__dict__)
    print("charge:", client.charge())

asyncio.run(main())
