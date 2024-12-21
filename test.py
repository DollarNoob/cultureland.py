import asyncio
import os
from dotenv import load_dotenv
from src.cultureland import Cultureland
from src.pin import Pin

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

    member_info = await client.get_member_info()
    print(member_info.__dict__)

    cash_logs = await client.get_culture_cash_logs(30)
    print(len(cash_logs))

    gift_limit = await client.get_gift_limit()
    print("Gift Limit:", gift_limit.limit)
    print("Remaining Limit:", gift_limit.remain)

    balance = await client.get_balance()
    print("Balance:", balance.balance)
    print("Safe Balance:", balance.safe_balance)
    print("Total Balance:", balance.total_balance)

    charge = await client.charge(Pin("3110-1234-1234-5678"))
    print("Charge Amount:", charge.amount)
    print("Charge Message:", charge.message)

    # voucher_logs = await client.check_voucher(Pin("3110-1234-1234-5678"))
    # print("Voucher Info:", voucher_logs.__dict__)
    # print("Voucher Spend History:", voucher_logs.spend_history[0].__dict__)

asyncio.run(main())
