# 작업중입니다.

import re
import httpx
import time
import math
import json
from bs4 import BeautifulSoup
from typing import Optional, Union
from urllib import parse
from datetime import datetime
from pin import Pin
from mTranskey import mTranskey
from _types import VoucherResponse, VoucherResultOther, SpendHistory, CulturelandVoucher, BalanceResponse, CulturelandBalance

class Cultureland:
    """
    컬쳐랜드 모바일웹을 자동화해주는 비공식 라이브러리입니다.
    로그인, 잔액조회, 충전, 선물 등 자주 사용되는 대부분의 기능을 지원합니다.
    """

    __id: str
    __password: str
    __keepLoginInfo: str
    __userInfo: str

    def __init__(self, client: Optional[httpx.Client] = None):
        self.__client = client or httpx.AsyncClient(
            base_url="https://m.cultureland.co.kr",
            headers={
                "User-Agent": "cultureland.py/1.0.0"
            }
        )

        if client:
            self.__client._base_url = "https://m.cultureland.co.kr"

    @property
    def client(self):
        return self.__client

    @property
    def id(self):
        return self.__id

    @property
    def password(self):
        return self.__password

    @property
    def keepLoginInfo(self):
        return self.__keepLoginInfo

    @property
    def userInfo(self):
        return self.__userInfo

    async def check_voucher(self, pin: Pin):
        if not await self.isLogin():
            raise Exception("로그인이 필요한 서비스 입니다.")

        # 핀번호가 유효하지 않거나 41로 시작하지 않거나 311~319로 시작하지 않는다면 리턴
        # /assets/js/egovframework/com/cland/was/util/ClandCmmUtl.js L1281
        if not pin.parts or not (pin.parts[0].startswith("41") or (pin.parts[0].startswith("31") and pin.parts[0][2] != "0")):
            raise Exception("정확한 모바일 상품권 번호를 입력하세요.")

        transkey = mTranskey(self.__client)
        servlet_data = transkey.get_servlet_data()

        # <input type="tel" title="네 번째 6자리 입력" id="input-14" name="culturelandInput">
        keypad = transkey.create_keypad(servlet_data, "number", "input-14", "culturelandInput", "tel");
        keypadLayout = keypad.get_keypad_layout()
        encrypted_pin, encrypted_hmac = keypad.encrypt_password(pin.parts[3], keypadLayout)

        payload = {
            "culturelandNo": pin.parts[0] + pin.parts[1] + pin.parts[2],
            "seedKey": transkey.encrypted_session_key,
            "initTime": servlet_data.get("init_time"),
            "keyIndex_input-14": keypad.key_index,
            "keyboardType_input-14": keypad.keyboard_type + "Mobile",
            "fieldType_input-14": keypad.field_type,
            "transkeyUuid": transkey.transkey_uuid,
            "transkey_input-14": encrypted_pin,
            "transkey_HM_input-14": encrypted_hmac
        }

        voucher_data_request = await self.client.post(
            "/vchr/getVoucherCheckMobileUsed.json",
            data=payload,
            headers={
                "Referer": "https://m.cultureland.co.kr/vchr/voucherUsageGiftM.do"
            }
        )

        voucher_data = VoucherResponse(voucher_data_request.json())

        if voucher_data.resultCd != "0":
            if voucher_data.resultCd == "1":
                raise Exception("일일 조회수를 초과하셨습니다.")
            else:
                raise Exception("잘못된 응답이 반환되었습니다.")

        result_other = list(map(VoucherResultOther, json.dumps(voucher_data.resultOther)))

        spend_history = []
        for result in voucher_data.resultMsg:
            spend_history.append(SpendHistory(
                title=result.item.GCSubMemberName,
                merchant_name=result.item.Store_name,
                amount=int(result.item.levyamount),
                timestamp=int(datetime.strptime(result.item.LevyDate + result.item.LevyTime, "").timestamp())
            )) # 파이썬은 숫자가 int 최대치를 초과할 경우 자동으로 long으로 변환

        return CulturelandVoucher(
            amount=result_other[0].FaceValue,
            balance=result_other[0].Balance,
            cert_no=result_other[0].CertNo,
            created_date=result_other[0].RegDate,
            expiry_date=result_other[0].ExpiryDate,
            spend_history=spend_history
        )

    async def get_balance(self):
        """
        컬쳐랜드 계정의 컬쳐캐쉬 잔액을 가져옵니다.

        ```py
        await client.get_balance()
        ```

        반환값:
            보유 잔액 정보
        """

        if not await self.is_login():
            raise Exception("로그인이 필요한 서비스 입니다.")

        balance_request = await self.client.post("/tgl/getBalance.json")

        balance = BalanceResponse(**balance_request.json())
        if balance.resultMessage != "성공":
            if balance.resultMessage:
                raise Exception(balance.resultMessage)
            else:
                raise Exception("잘못된 응답이 반환되었습니다.")

        return CulturelandBalance(
            balance=int(balance.blnAmt),
            safe_balance=int(balance.bnkAmt),
            total_balance=int(balance.myCash)
        )

    async def charge(self, pins: Union[Pin, list[Pin]]):
        if not await self.is_login():
            raise Exception("로그인이 필요한 서비스 입니다.")

        if not isinstance(pins, list):
            pins = [ pins ]

        if len(pins) == 0 or len(pins) > 10:
            raise ValueError("핀번호는 1개 이상, 10개 이하여야 합니다.")

        only_mobile_vouchers = all(len(pin.parts[3]) == 4 for pin in pins) # 모바일문화상품권만 있는지

        # 선행 페이지 요청을 보내지 않으면 잘못된 접근 오류 발생
        await self.__client.get(
            "/csh/cshGiftCard.do" if only_mobile_vouchers # 모바일문화상품권
            else "/csh/cshGiftCardOnline.do" # 문화상품권(18자리)
        ) # 문화상품권(18자리)에서 모바일문화상품권도 충전 가능, 모바일문화상품권에서 문화상품권(18자리) 충전 불가능

        transkey = mTranskey(self.__client)
        servlet_data = await transkey.get_servlet_data()

        payload = {
            "seedKey": transkey.encrypted_session_key,
            "initTime": servlet_data.get("init_time"),
            "transkeyUuid": transkey.transkey_uuid
        }

        for i in range(len(pins)):
            pin = pins[i]

            parts = pin.parts or ["", "", "", ""]
            pin_count = i + 1 # scr0x이 아닌 scr1x부터 시작하기 때문에 1부터 시작

            txtScr4 = f"txtScr{pin_count}4"

            # <input type="password" name="{scr4}" id="{txtScr4}">
            keypad = transkey.create_keypad(servlet_data, "number", txtScr4, f"scr{pin_count}4")
            keypad_layout = await keypad.get_keypad_layout()
            encrypted_pin, encrypted_hmac = keypad.encrypt_password(parts[3], keypad_layout)

            # scratch (핀번호)
            payload[f"scr{pin_count}1"] = parts[0]
            payload[f"scr{pin_count}2"] = parts[1]
            payload[f"scr{pin_count}3"] = parts[2]

            # keyboard
            payload["keyIndex_" + txtScr4] = keypad.key_index
            payload["keyboardType_" + txtScr4] = keypad.keyboard_type + "Mobile"
            payload["fieldType_" + txtScr4] = keypad.field_type

            # transkey
            payload["transkey_" + txtScr4] = encrypted_pin
            payload["transkey_HM_" + txtScr4] = encrypted_hmac

        charge_request = await self.__client.post(
            "/csh/cshGiftCardProcess.do" if only_mobile_vouchers # 모바일문화상품권
            else "/csh/cshGiftCardOnlineProcess.do", # 문화상품권(18자리)
            data=payload,
            follow_redirects=False
        )

        charge_result_request = await self.__client.get(charge_request.headers.get("location")) # 충전 결과 받아오기

        parsed_results = BeautifulSoup(charge_result_request.text, "html.parser") # 충전 결과 HTML 파싱
        parsed_results = parsed_results.find("tbody").find_all("tr")

        results = []
        for i in range(len(pins)):
            charge_result = parsed_results[i].find_all("td")

            results.append({
                "message": charge_result[2].text,
                "amount": int(charge_result[3].text.replace(",", "").replace("원", ""))
            })

        return results[0] if len(results) == 1 else results

    async def is_login(self) -> bool:
        """
        현재 세션이 컬쳐랜드에 로그인되어 있는지 확인합니다.

        ```py
        await client.is_login() # True | False
        ```

        반환값:
            로그인 여부
        """

        is_login_request = await self.client.post("/mmb/isLogin.json")
        is_login = is_login_request.json()
        return is_login

    async def login(self, keepLoginInfo: str) -> bool:
        self.client.cookies.set("KeepLoginConfig", keepLoginInfo, "m.cultureland.co.kr")

        user_id_request = await self.client.get(
            "/mmb/loginMain.do",
            headers={
                "Referer": "https://m.cultureland.co.kr/index.do"
            }
        )

        user_id_regex = re.compile('<input type="text" id="txtUserId" name="userId" value="(\\w*)" maxlength="12" oninput="maxLengthCheck\\(this\\);" placeholder="아이디" >')
        user_id_match = user_id_regex.search(user_id_request.text)

        if user_id_match is None:
            raise Exception("입력하신 로그인 유지 정보는 만료된 정보입니다.")

        login_request = await self.client.post(
            "/mmb/loginProcess.do",
            headers={
                "Referer": "https://m.cultureland.co.kr/mmb/loginMain.do"
            },
            data={
                "keepLoginInfo": keepLoginInfo,
                "userId": user_id_match[1],
                "keepLogin": "Y"
            },
            follow_redirects=False
        )

        self.user_id = user_id_match[1]
        return True

    