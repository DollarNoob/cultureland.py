import asyncio
import os
from dotenv import load_dotenv
from cultureland import Cultureland
from pin import Pin

load_dotenv()

async def main():
    client = Cultureland()

    print("Using IDP")
    login = await client.login(os.getenv("CULTURELAND_ID"), os.getenv("CULTURELAND_PASSWORD"))
    print("KeepLoginInfo:", login.keep_login_info)
    print("User ID:", login.user_id)

    client.client.cookies.clear()

    print("Using KeepLoginInfo")
    login = await client.login(login.keep_login_info)
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
