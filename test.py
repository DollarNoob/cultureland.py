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

    login = await client.login(os.getenv("CULTURELAND_KEEP_LOGIN_INFO"))
    print("KeepLoginInfo:", login.keep_login_info)
    print("User ID:", login.user_id)

    is_login = await client.is_login()
    print("Is Logged In:", is_login)

    user_info = await client.get_user_info()
    print(user_info.__dict__)

    balance = await client.get_balance()
    print("Balance:", balance.balance)
    print("Safe Balance:", balance.safe_balance)
    print("Total Balance:", balance.total_balance)

    charge = await client.charge(Pin("3110-1234-1234-5678"))
    print("Charge Amount:", charge.amount)
    print("Charge Message:", charge.message)

asyncio.run(main())
