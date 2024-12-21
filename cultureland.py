# 작업중입니다.

import re
import httpx
import time
import math
import json
import base64
import os
from bs4 import BeautifulSoup
from typing import Optional, Union
from urllib import parse
from datetime import datetime
from pin import Pin
from mTranskey import mTranskey
from _types import VoucherResponse, VoucherResultOther, SpendHistory, CulturelandVoucher, BalanceResponse, CulturelandBalance, CulturelandCharge, UserInfoResponse, CulturelandUser, CulturelandMember, CashLogsResponse, CulturelandCashLog, CulturelandLogin

class Cultureland:
    """
    컬쳐랜드 모바일웹을 자동화해주는 비공식 라이브러리입니다.
    로그인, 잔액조회, 충전, 선물 등 자주 사용되는 대부분의 기능을 지원합니다.
    """

    __id: str
    __password: str | None
    __keep_login_info: str
    __user_info: CulturelandUser

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
    def keep_login_info(self):
        return self.__keep_login_info

    @property
    def user_info(self):
        return self.__user_info

    async def check_voucher(self, pin: Pin):
        """
        컬쳐랜드상품권(모바일문화상품권, 16자리)의 정보를 가져옵니다.
        로그인이 필요합니다.
        계정당 일일 조회수 10회 한도가 있습니다.

        파라미터:
            * pin (Pin): 상품권의 핀번호

        ```py
        await client.check_voucher(Pin("3110-0123-4567-8901"))
        ```

        반환값:
            * amount (int): 상품권의 금액
            * balance (int): 상품권의 잔액
            * cert_no (str): 상품권의 발행번호 (인증번호)
            * created_date (str): 상품권의 발행일 | `20241231`
            * expiry_date (str): 상품권의 만료일 | `20291231`
            * spend_history (list[SpendHistory]): 상품권 사용 내역
                * title (str): 내역 제목
                * merchant_name (str): 사용 가맹점 이름
                * amount (int): 사용 금액
                * timestamp (int): 사용 시각 (Unix Timestamp)
        """

        if not await self.is_login():
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

        voucher_data_request = await self.__client.post(
            "/vchr/getVoucherCheckMobileUsed.json",
            data=payload,
            headers={
                "Referer": str(self.__client.base_url.join("/vchr/voucherUsageGiftM.do"))
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
                timestamp=int(datetime.strptime(result.item.LevyDate + result.item.LevyTime, "TODO").timestamp())
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
            * balance (int): 사용 가능 금액
            * safe_balance (int): 보관중인 금액 (안심금고)
            * total_balance (int): 총 잔액 (사용 가능 금액 + 보관중인 금액)
        """

        if not await self.is_login():
            raise Exception("로그인이 필요한 서비스 입니다.")

        balance_request = await self.__client.post("/tgl/getBalance.json")

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
        """
        컬쳐랜드상품권(모바일문화상품권) 및 문화상품권(18자리)을 컬쳐캐쉬로 충전합니다.
        지류/온라인문화상품권(18자리)은 2022.12.31 이전 발행 건만 충전 가능합니다.

        파라미터:
            * pins (Pin | list[Pin]): 상품권의 핀번호

        ```py
        # 한 개의 핀번호 충전
        charge_one = await client.charge(Pin("3110-0123-4567-8901"))
        print(charge_one.message) # 충전 완료

        # 여러개의 핀번호 충전
        charge_many = await client.charge([
            Pin("3110-0123-4567-8902"),
            Pin("3110-0123-4567-8903")
        ])
        print(charge_many[0].message) # 충전 완료
        print(charge_many[1].message) # 상품권지갑 보관
        ```

        반환값:
            * message (str): 성공 여부 메시지 `충전 완료` | `상품권지갑 보관` | `잔액이 0원인 상품권` | `상품권 번호 불일치` | `등록제한(20번 등록실패)`
            * amount (int): 충전 금액
        """

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

        results: list[CulturelandCharge] = []
        for i in range(len(pins)):
            charge_result = parsed_results[i].find_all("td")

            results.append(CulturelandCharge(
                message=charge_result[2].text,
                amount=int(charge_result[3].text.replace(",", "").replace("원", ""))
            ))

        return results[0] if len(results) == 1 else results

    """
    /**
     * 컬쳐캐쉬를 사용해 컬쳐랜드상품권(모바일문화상품권)을 본인 번호로 선물합니다.
     * @param amount 구매 금액 (최소 1천원부터 최대 5만원까지 100원 단위로 입력 가능)
     * @param quantity 구매 수량 (최대 5개)
     * @example
     * // 5000원권 1장을 나에게 선물
     * await client.gift(5000, 1);
     * @returns 선물 결과
     */
    public async gift(amount: number, quantity = 1): Promise<CulturelandGift> {
        if (!(await this.isLogin())) throw new CulturelandError("LoginRequiredError", "로그인이 필요한 서비스 입니다.");

        // 구매 금액이 조건에 맞지 않을 때
        if (amount % 100 !== 0 || amount < 1000 || amount > 50000) throw new CulturelandError("RangeError", "구매 금액은 최소 1천원부터 최대 5만원까지 100원 단위로 입력 가능합니다.");

        // 구매 수량이 조건에 맞지 않을 때
        if (quantity % 1 !== 0 || quantity < 1 || quantity > 5) throw new CulturelandError("RangeError", "구매 수량은 최소 1개부터 최대 5개까지 정수로 입력 가능합니다.");

        // 유저정보 가져오기 (선물구매에 userKey 필요)
        const userInfo = await this.getUserInfo();

        // 선행 페이지 요청을 보내지 않으면 잘못된 접근 오류 발생
        await this.client.get("https://m.cultureland.co.kr/gft/gftPhoneApp.do");

        // 내폰으로 전송 (본인 번호 가져옴)
        const phoneInfoRequest = await this.client.post("https://m.cultureland.co.kr/cpn/getGoogleRecvInfo.json", new URLSearchParams({
            sendType: "LMS",
            recvType: "M",
            cpnType: "GIFT"
        }), {
            headers: {
                "Referer": "https://m.cultureland.co.kr/gft/gftPhoneApp.do"
            }
        });

        const phoneInfo: PhoneInfoResponse = await phoneInfoRequest.json();
        if (phoneInfo.errMsg !== "정상") {
            if (phoneInfo.errMsg) throw new CulturelandError("LookupError", phoneInfo.errMsg);
            else throw new CulturelandError("ResponseError", "잘못된 응답이 반환되었습니다.");
        }

        const sendGiftRequest = await this.client.post("https://m.cultureland.co.kr/gft/gftPhoneCashProc.do", new URLSearchParams({
            revEmail: "",
            sendType: "S",
            userKey: userInfo.userKey!.toString(),
            limitGiftBank: "N",
            bankRM: "OK",
            giftCategory: "M",
            quantity: quantity.toString(),
            amount: amount.toString(),
            chkLms: "M",
            revPhone: phoneInfo.hpNo1 + phoneInfo.hpNo2 + phoneInfo.hpNo3,
            paymentType: "cash",
            agree: "on"
        }), {
            redirect: "manual"
        });

        const giftResultRequest = await this.client.get("https://m.cultureland.co.kr" + sendGiftRequest.headers.get("location"));

        const giftResult: string = await giftResultRequest.text(); // 선물 결과 받아오기

        // 컬쳐랜드상품권(모바일문화상품권) 선물(구매)가 완료되었습니다.
        if (giftResult.includes("<strong> 컬쳐랜드상품권(모바일문화상품권) 선물(구매)가<br />완료되었습니다.</strong>")) {
            // 바코드의 코드 (URL 쿼리: code)
            const barcodeCode = giftResult.match(/<input type="hidden" id="barcodeImage"      name="barcodeImage"       value="https:\/\/m\.cultureland\.co\.kr\/csh\/mb\.do\?code=([\w/+=]+)" \/>/)?.[1];
            if (!barcodeCode) throw new CulturelandError("ResponseError", "선물 결과에서 바코드 URL을 찾을 수 없습니다.");

            // 핀번호(바코드 번호)를 가져오기 위해 바코드 정보 요청
            const barcodePath = "/csh/mb.do?code=" + barcodeCode;
            const barcodeDataRequest = await this.client.get("https://m.cultureland.co.kr" + barcodePath);

            const barcodeData: string = await barcodeDataRequest.text();

            // 선물 결과에서 핀번호(바코드 번호) 파싱
            const pinCode: string = barcodeData
                .split("<span>바코드번호</span>")[1]
                .split("</span>")[0]
                .split("<span>")[1];

            return {
                pin: new Pin(pinCode),
                url: "https://m.cultureland.co.kr" + barcodePath
            };
        }

        // 컬쳐랜드상품권(모바일문화상품권) 선물(구매)가 실패 하였습니다.
        const failReason = giftResult.match(/<dt class="two">실패 사유 <span class="right">(.*)<\/span><\/dt>/)?.[1]?.replace(/<br>/g, " ");
        if (failReason) throw new CulturelandError("PurchaseError", failReason);
        else throw new CulturelandError("ResponseError", "잘못된 응답이 반환되었습니다.");
    }

    /**
     * 선물하기 API에서 선물 한도를 가져옵니다.
     * @example
     * await client.getGiftLimit();
     * @returns 선물 한도
     */
    public async getGiftLimit(): Promise<CulturelandGiftLimit> {
        if (!(await this.isLogin())) throw new CulturelandError("LoginRequiredError", "로그인이 필요한 서비스 입니다.");

        const limitInfoRequest = await this.client.post("https://m.cultureland.co.kr/gft/chkGiftLimitAmt.json");

        const limitInfo: GiftLimitResponse = await limitInfoRequest.json();
        if (limitInfo.errMsg !== "정상") {
            if (limitInfo.errMsg) throw new CulturelandError("LookupError", limitInfo.errMsg);
            else throw new CulturelandError("ResponseError", "잘못된 응답이 반환되었습니다.");
        }

        return {
            remain: limitInfo.giftVO.ccashRemainAmt,
            limit: limitInfo.giftVO.ccashLimitAmt
        };
    }
    """

    async def get_user_info(self):
        """
        안심금고 API에서 유저 정보를 가져옵니다.

        ```py
        await client.get_user_info()
        ```

        반환값:
            * phone (str): 휴대폰 번호
            * safe_level (int): 안심금고 레벨
            * safe_password (bool): 안심금고 비밀번호 여부
            * register_date (int): 가입 시각 (Unix Timestamp)
            * user_id (str): 컬쳐랜드 ID
            * user_key (str): 유저 고유 번호
            * user_ip (str): 접속 IP
            * index (int): 유저 고유 인덱스
            * category (str): 유저 종류
        """

        if not await self.is_login():
            raise Exception("로그인이 필요한 서비스 입니다.")

        user_info_request = await self.__client.post("/tgl/flagSecCash.json")

        user_info = UserInfoResponse(**user_info_request.json())
        if user_info.resultMessage != "성공":
            if not user_info.resultMessage:
                raise Exception("잘못된 응답이 반환되었습니다.")
            else:
                raise Exception(user_info.resultMessage)

        return CulturelandUser(
            phone=user_info.Phone,
            safe_level=int(user_info.SafeLevel),
            safe_password=(user_info.CashPwd != "0"),
            register_date=int(datetime.strptime(user_info.RegDate, "%Y-%m-%d %H:%M:%S.%f").timestamp()),
            user_id=user_info.userId,
            user_key=user_info.userKey,
            user_ip=user_info.userIp,
            index=int(user_info.idx),
            category=user_info.category
        )

    async def get_member_info(self):
        """
        내정보 페이지에서 멤버 정보를 가져옵니다.

        ```py
        await client.get_member_info()
        ```

        반환값:
            * id (str): 컬쳐랜드 ID
            * name (str): 멤버의 이름 | `홍*동`
            * verification_level (str): 멤버의 인증 등급
        """

        if not await self.is_login():
            raise Exception("로그인이 필요한 서비스 입니다.")

        member_info_request = await self.__client.post("/mmb/mmbMain.do")
        member_info = member_info_request.text

        if "meTop_info" not in member_info:
            raise Exception("멤버 정보를 가져올 수 없습니다.")

        member_data = BeautifulSoup(member_info) # 멤버 정보 HTML 파싱
        member_data = member_data.find("div", id="meTop_info")

        span = member_data.find("span")
        strong = member_data.find("strong")
        p = member_data.find("p")

        return CulturelandMember(
            id=None if not span else span.text,
            name=None if not strong else strong.text.strip(),
            verification_level=None if not p else p.text
        )

    async def get_culture_cash_logs(self, days: int, page_size = 20, page = 1):
        """
        컬쳐캐쉬 충전 / 사용 내역을 가져옵니다.

        파라미터:
            * days (int): 조회 일수
            * page_size (int): 한 페이지에 담길 내역 수 (default: 20)
            * page (int): 페이지 (default: 1)

        ```py
        # 최근 30일간의 내역 중 1페이지의 내역
        await client.get_culture_cash_logs(30, 20, 1)
        ```

        반환값:
            * title (str): 내역 제목
            * merchant_code (str): 사용 가맹점 코드
            * merchant_name (str): 사용 가맹점 이름
            * amount (int): 사용 금액
            * balance (int): 사용 후 남은 잔액
            * spend_type (str): 사용 종류 `사용` | `사용취소` | `충전`
            * timestamp (int): 사용 시각 (Unix Timestamp)
        """

        if not await self.is_login():
            raise Exception("로그인이 필요한 서비스 입니다.")

        cash_logs_request = await self.__client.post(
            "/tgl/cashList.json",
            data={
                "addDay": days - 1,
                "pageSize": page_size,
                "page": page
            },
            headers={
                "Referer": str(self.__client.base_url.join("/tgl/cashSearch.do"))
            }
        )

        cash_logs = list(map(CashLogsResponse, cash_logs_request.json()))
        cultureland_cash_logs: list[CulturelandCashLog] = []
        for log in cash_logs:
            cultureland_cash_logs.append(CulturelandCashLog(
                title=log.item.Note,
                merchant_code=log.item.memberCode,
                merchant_name=log.item.memberName,
                amount=int(log.item.inAmount) - int(log.item.outAmount),
                balance=int(log.item.balance),
                spend_type=log.item.accType,
                timestamp=int(datetime.strptime(log.item.accDate + log.item.accTime, "%Y%m%d%H%M%S").timestamp())
            ))

        return cultureland_cash_logs

    async def is_login(self) -> bool:
        """
        현재 세션이 컬쳐랜드에 로그인되어 있는지 확인합니다.

        ```py
        await client.is_login() # True | False
        ```

        반환값:
            로그인 여부 (bool)
        """

        is_login_request = await self.__client.post("/mmb/isLogin.json")
        is_login = is_login_request.json()
        return is_login

    async def login(self, id: str, password: Optional[str] = None):
        """
        ID와 비밀번호 또는 로그인 유지 쿠키로 컬쳐랜드에 로그인합니다.

        파라미터:
            * id (str): 컬쳐랜드 ID (비밀번호 필요) / 로그인 유지 쿠키 (비밀번호 불필요)
            * password (str | None): 컬쳐랜드 비밀번호 (ID 입력시 필수)

        ```py
        await client.login("test1234", "test1234!") # ID와 비밀번호로 로그인
        await client.login("keep_login_info") # 로그인 유지 쿠키로 로그인
        ```

        반환값:
            * user_id (str): 컬쳐랜드 ID
            * keep_login_info (str): 로그인 유지 쿠키
        """

        is_idp_login = isinstance(password, str)
        keep_login_info = None if is_idp_login else parse.unquote(id)
        _id = id if is_idp_login else None

        # KeepLoginConfig 쿠키를 사용할 경우 hCaptcha 값의 유효성을 확인하지 않는 취약점 사용
        self.__client.cookies.set(
            "KeepLoginConfig",
            base64.urlsafe_b64encode(os.urandom(48)) if is_idp_login else keep_login_info,
            "m.cultureland.co.kr"
        )

        if is_idp_login:
            if len(id) == 0:
                raise ValueError("아이디를 입력해 주십시오.")
            elif len(password) == 0:
                raise ValueError("비밀번호를 입력해 주십시오.")
        else:
            login_main_request = await self.__client.get(
                "/mmb/loginMain.do",
                headers={
                    "Referer": str(self.__client.base_url.join("/index.do"))
                }
            )

            user_id_regex = re.compile('<input type="text" id="txtUserId" name="userId" value="(\\w*)" maxlength="12" oninput="maxLengthCheck\\(this\\);" placeholder="아이디" >')
            user_id_match = user_id_regex.search(login_main_request.text)

            if user_id_match is None:
                raise Exception("입력하신 로그인 유지 정보는 만료된 정보입니다.")
            _id = user_id_match[1]

        transkey = mTranskey(self.__client)
        servlet_data = await transkey.get_servlet_data()

        keypad = transkey.create_keypad(servlet_data, "qwerty", "passwd", "passwd")
        keypad_layout = await keypad.get_keypad_layout()
        encrypted_password, encrypted_hmac = keypad.encrypt_password(password if is_idp_login else "", keypad_layout)

        payload = {
            "keepLoginInfo": "" if is_idp_login else keep_login_info,
            "userId": _id,
            "keepLogin": "Y",
            "seedKey": transkey.encrypted_session_key,
            "initTime": servlet_data.get("init_time"),
            "keyIndex_passwd": keypad.key_index,
            "keyboardType_passwd": keypad.keyboard_type + "Mobile",
            "fieldType_passwd": keypad.field_type,
            "transkeyUuid": transkey.transkey_uuid,
            "transkey_passwd": encrypted_password,
            "transkey_HM_passwd": encrypted_hmac
        }

        login_request = await self.__client.post(
            "/mmb/loginProcess.do",
            data=payload,
            headers={
                "Referer": str(self.__client.base_url.join("/mmb/loginMain.do"))
            },
            follow_redirects=False
        )

        # 메인 페이지로 리다이렉트되지 않은 경우
        if login_request.status_code == 200:
            login_data = login_request.text
            error_message_regex = re.compile('<input type="hidden" name="loginErrMsg"  value="([^"]+)" \\/>')
            error_message = error_message_regex.search(login_data)
            if not error_message:
                raise Exception("잘못된 응답이 반환되었습니다.")
            else:
                raise Exception(error_message.replace("\\n\\n", ". "))

        # 컬쳐랜드 로그인 정책에 따라 로그인이 제한된 경우
        if login_request.headers.get("location") == "/cmp/authConfirm.do":
            error_page_request = await self.__client.get(login_request.headers.get("location"))

            # 제한코드 가져오기
            error_code_regex = re.compile('var errCode = "(\\d+)";')
            error_code = error_code_regex.search(error_page_request.text)
            if not error_code:
                raise Exception("컬쳐랜드 로그인 정책에 따라 로그인이 제한되었습니다.")
            else:
                raise Exception(f"컬쳐랜드 로그인 정책에 따라 로그인이 제한되었습니다. (제한코드: {error_code})")

        # 로그인 유지 정보 가져오기
        cookies = login_request.headers.get_list("set-cookie")
        for cookie in cookies:
            if cookie.startswith("KeepLoginConfig="):
                keep_login_info = parse.unquote(cookie.split(";")[0].split("=")[1])
                break

        if not keep_login_info:
            raise Exception("잘못된 응답이 반환되었습니다.")

        self.__userInfo = await self.get_user_info()

        # 변수 저장
        self.__id = _id
        self.__password = password if is_idp_login else None
        self.__keep_login_info = keep_login_info

        return CulturelandLogin(
            user_id=_id,
            keep_login_info=keep_login_info
        )
