from dataclasses import dataclass
from typing import Literal, Optional

class VoucherResultItem:
    LevyTime: str
    GCSubMemberName: str
    State: str
    levyamount: str
    Store_name: str
    LevyDate: str

class VoucherResult:
    item: VoucherResultItem

@dataclass
class VoucherResponse:
    resultCd: str
    resultOther: str
    resultMsg: list[VoucherResult]

class VoucherResultOther:
    FaceValue: int
    ExpiryDate: str
    RegDate: str
    State: str
    CertNo: str
    Balance: int

class SpendHistory:
    def __init__(self, title: str, merchant_name: str, amount: int, timestamp: int):
       self.__title = title
       self.__merchant_name = merchant_name
       self.__amount = amount
       self.__timestamp = timestamp

    @property
    def title(self):
        """
        내역 제목
        """
        return self.__title

    @property
    def merchant_name(self):
        """
        사용 가맹점 이름
        """
        return self.__merchant_name

    @property
    def amount(self):
        """
        사용 금액
        """
        return self.__amount

    @property
    def timestamp(self):
        """
        사용 시각 (Unix Timestamp)
        """
        return self.__timestamp

class CulturelandVoucher:
    def __init__(self, amount: int, balance: int, cert_no: str, created_date: str, expiry_date: str, spend_history: list[SpendHistory]):
        self.__amount = amount
        self.__balance = balance
        self.__cert_no = cert_no
        self.__created_date = created_date
        self.__expiry_date = expiry_date
        self.__spend_history = spend_history

    @property
    def amount(self):
        """
        상품권의 금액
        """
        return self.__amount

    @property
    def balance(self):
        """
        상품권의 잔액
        """
        return self.__balance

    @property
    def cert_no(self):
        """
        상품권의 발행번호 (인증번호)
        """
        return self.__cert_no

    @property
    def created_date(self):
        """
        상품권의 발행일 | `20241231`
        """
        return self.__created_date

    @property
    def expiry_date(self):
        """
        상품권의 만료일 | `20291231`
        """
        return self.__expiry_date

    @property
    def spend_history(self):
        """
        상품권 사용 내역
        """
        return self.__spend_history

@dataclass
class BalanceResponse:
    safeDelYn: Literal["Y", "N"]
    memberKind: str
    casChargeYN: Literal["Y", "N"]
    resultCode: str
    resultMessage: str
    blnWaitCash: str
    walletPinYN: Literal["Y", "N"]
    bnkAmt: str
    remainCash: str
    transCash: str
    kycYN: str
    myCash: str
    blnAmt: str
    walletYN: Literal["Y", "N"]
    limitCash: str

class CulturelandBalance:
    def __init__(self, balance: int, safe_balance: int, total_balance: int):
        self.__balance = balance
        self.__safe_balance = safe_balance
        self.__total_balance = total_balance

    @property
    def balance(self):
        """
        사용 가능 금액
        """
        return self.__balance

    @property
    def safe_balance(self):
        """
        보관중인 금액 (안심금고)
        """
        return self.__safe_balance

    @property
    def total_balance(self):
        """
        총 잔액 (사용 가능 금액 + 보관중인 금액)
        """
        return self.__total_balance


class CulturelandCharge:
    def __init__(self, message: Literal["충전 완료", "상품권지갑 보관", "잔액이 0원인 상품권", "상품권 번호 불일치", "등록제한(20번 등록실패)"], amount: int):
        self.__message = message
        self.__amount = amount

    @property
    def message(self):
        """
        성공 여부 메시지

        `충전 완료` | `상품권지갑 보관` | `잔액이 0원인 상품권` | `상품권 번호 불일치` | `등록제한(20번 등록실패)`
        """
        return self.__message

    @property
    def amount(self):
        """
        충전 금액
        """
        return self.__amount

"""
export interface PhoneInfoResponse {
    recvType: str
    email2: str
    errCd: str
    email1: str
    hpNo2: str
    hpNo1: str
    hpNo3: str
    errMsg: str
    sendType: str
}

export interface CulturelandGift {
    /**
     * 선물 바코드 번호
     */
    pin: Pin;
    /**
     * 선물 바코드 URL
     */
    url: str
}

export interface GiftLimitResponse {
    errCd: str
    giftVO: {
        maxAmount: number;
        custCd: null;
        balanceAmt: number;
        safeAmt: number;
        cashGiftRemainAmt: number;
        cashGiftSumGift: number;
        cashGiftNoLimitYn: Literal["Y", "N"]
        cashGiftNoLimitUserYn: str
        cashGiftLimitAmt: number;
        cashGiftMGiftRemainDay: number;
        cashGiftMGiftRemainMon: number;
        toUserId: null;
        toUserNm: null;
        toMsg: null;
        transType: null;
        timestamp: null;
        certValue: null;
        revPhone: null;
        paymentType: null;
        sendType: null;
        sendTypeNm: null;
        giftCategory: null;
        sendTitl: null;
        amount: number;
        quantity: number;
        controlCd: null;
        lgControlCd: null;
        contentsCd: null;
        contentsNm: null;
        svrGubun: null;
        payType: null;
        levyDate: null;
        levyTime: null;
        levyDateTime: null;
        genreDtl: null;
        faceValue: number;
        sendCnt: number;
        balance: number;
        state: null;
        lgState: null;
        dtlState: null;
        selType: null;
        strPaymentType: null;
        strSendType: null;
        strRcvInfo: null;
        appUseYn: null;
        reSendYn: null;
        reSendState: null;
        strReSendState: null;
        cnclState: null;
        strCnclState: null;
        page: number;
        pageSize: number;
        totalCnt: number;
        totalSum: number;
        totalCntPage: number;
        isLastPageYn: null;
        reSendType: null;
        reSvrGubun: null;
        aESImage: null;
        sendUserId: null;
        sendUserNm: null;
        rcvUserKey: null;
        rcvUserID: null;
        rcvName: null;
        rcvHpno: null;
        sendMsg: null;
        giftType: null;
        sendDate: null;
        receiveDate: null;
        expireDate: null;
        cancelDate: null;
        cancelType: null;
        regdate: null;
        waitPage: number;
        sendPage: number;
        waitCnt: number;
        cancelCnt: number;
        transCnt: number;
        successCnt: number;
        nbankMGiftRemainDay: number;
        nbankNoLimitUserYn: str
        nbankNoLimitYn: Literal["Y", "N"]
        ccashNoLimitUserYn: str
        ccashRemainAmt: number;
        ccashMGiftRemainMon: number;
        ccashMGiftRemainDay: number;
        nbankRemainAmt: number;
        rtimeNoLimitUserYn: str
        ccashNoLimitYn: Literal["Y", "N"]
        nbankMGiftRemainMon: number;
        rtimeMGiftRemainMon: number;
        rtimeMGiftRemainDay: number;
        rtimeNoLimitYn: Literal["Y", "N"]
        rtimeRemainAmt: number;
        nbankLimitAmt: number;
        rtimeSumGift: number;
        ccashLimitAmt: number;
        nbankSumGift: number;
        nbankSumVacnt: number;
        rtimeLimitAmt: number;
        ccashSumGift: number;
    };
    errMsg: str
}

export interface CulturelandGiftLimit {
    /**
     * 잔여 선물 한도
     */
    remain: number;
    /**
     * 최대 선물 한도
     */
    limit: number;
}


"""

@dataclass
class UserInfoResponse:
    Del_Yn: Literal["Y", "N"]
    callUrl: str
    custCd: str
    certVal: str
    backUrl: str
    authDttm: str
    resultCode: str
    user_key: str
    Status_M: str
    Phone: str
    Status_Y: str
    Status_W: str
    Status: str
    SafeLevel: str
    Status_D: str
    CashPwd: str
    RegDate: str
    resultMessage: str
    userId: str
    userKey: str
    Proc_Date: str
    size: int
    user_id: str
    succUrl: str
    userIp: str
    Mobile_Yn: Literal["Y", "N"]
    idx: str
    category: str

class CulturelandUser:
    def __init__(self, phone: str, safe_level: int, safe_password: bool, register_date: int, user_id: str, user_key: str, user_ip: str, index: int, category: str):
        self.__phone = phone
        self.__safe_level = safe_level
        self.__safe_password = safe_password
        self.__register_date = register_date
        self.__user_id = user_id
        self.__user_key = user_key
        self.__user_ip = user_ip
        self.__index = index
        self.__category = category

    @property
    def phone(self):
        """
        휴대폰 번호
        """
        return self.__phone

    @property
    def safe_level(self):
        """
        안심금고 레벨
        """
        return self.__safe_level

    @property
    def safe_password(self):
        """
        안심금고 비밀번호 여부
        """
        return self.__safe_password

    @property
    def register_date(self):
        """
        가입 시각 (Unix Timestamp)
        """
        return self.__register_date

    @property
    def user_id(self):
        """
        컬쳐랜드 ID
        """
        return self.__user_id

    @property
    def user_key(self):
        """
        유저 고유 번호
        """
        return self.__user_key

    @property
    def user_ip(self):
        """
        접속 IP
        """
        return self.__user_ip

    @property
    def index(self):
        """
        유저 고유 인덱스
        """
        return self.__index

    @property
    def category(self):
        """
        유저 종류
        """
        return self.__category

class CulturelandMember:
    def __init__(self, id: Optional[str], name: Optional[str], verification_level: Optional[str]):
        self.__id = id
        self.__name = name
        self.__verification_level = verification_level

    @property
    def id(self):
        """
        컬쳐랜드 ID
        """
        return self.__id

    @property
    def name(self):
        """
        멤버의 이름 | `홍*동`
        """
        return self.__name

    @property
    def verification_level(self):
        """
        멤버의 인증 등급
        """
        return self.__verification_level

class CashLogItem:
    accDate: str
    memberCode: str
    outAmount: str
    balance: str
    inAmount: str
    NUM: str
    Note: str
    accTime: str
    memberName: str
    accType: str
    safeAmount: str

@dataclass
class CashLogsResponse:
    item: CashLogItem

class CulturelandCashLog:
    def __init__(self, title: str, merchant_code: str, merchant_name: str, amount: int, balance: int, spend_type: Literal["사용", "사용취소", "충전"], timestamp: int):
        self.__title = title
        self.__merchant_code = merchant_code
        self.__merchant_name = merchant_name
        self.__amount = amount
        self.__balance = balance
        self.__spend_type = spend_type
        self.__timestamp = timestamp

    @property
    def title(self):
        """
        내역 제목
        """
        return self.__title

    @property
    def merchant_code(self):
        """
        사용 가맹점 코드
        """
        return self.__merchant_code

    @property
    def merchant_name(self):
        """
        사용 가맹점 이름
        """
        return self.__merchant_name

    @property
    def amount(self):
        """
        사용 금액
        """
        return self.__amount

    @property
    def balance(self):
        """
        사용 후 남은 잔액
        """
        return self.__balance

    @property
    def spend_type(self):
        """
        사용 종류

        `사용` | `사용취소` | `충전`
        """
        return self.__spend_type

    @property
    def timestamp(self):
        """
        사용 시각 (Unix Timestamp)
        """
        return self.__timestamp

class CulturelandLogin:
    def __init__(self, user_id: str, keep_login_info: str):
        self.__user_id = user_id
        self.__keep_login_info = keep_login_info

    @property
    def user_id(self):
        """
        컬쳐랜드 ID
        """
        return self.__user_id

    @property
    def keep_login_info(self):
        """
        로그인 유지 쿠키
        """
        return self.__keep_login_info
