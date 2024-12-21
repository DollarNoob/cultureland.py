from dataclasses import dataclass
from typing import Literal

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
    """
    title (str): 내역 제목
    merchant_name (str): 사용 가맹점 이름
    amount (int): 사용 금액
    timestamp (int): 사용 시각 (UNIX Timestamp)
    """

    def __init__(self, title: str, merchant_name: str, amount: int, timestamp: int):
       self.title = title
       self.merchant_name = merchant_name
       self.amount = amount
       self.timestamp = timestamp

class CulturelandVoucher:
    """
    amount (int): 상품권의 금액
    balance (int): 상품권의 잔액
    cert_no (str): 상품권의 발행번호 (인증번호)
    created_date (str): 상품권의 발행일 | `20241231`
    expiry_date (str): 상품권의 만료일 | `20291231`
    spend_history (list[SpendHistory]): 상품권 사용 내역
    """

    def __init__(self, amount: int, balance: int, cert_no: str, created_date: str, expiry_date: str, spend_history: list[SpendHistory]):
        self.amount = amount
        self.balance = balance
        self.cert_no = cert_no
        self.created_date = created_date
        self.expiry_date = expiry_date
        self.spend_history = spend_history

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
    """
    balance (int): 사용 가능 금액
    safe_balance (int): 보관중인 금액 (안심금고)
    total_balance (int): 총 잔액 (사용 가능 금액 + 보관중인 금액)
    """

    def __init__(self, balance: int, safe_balance: int, total_balance: int):
        self.balance = balance
        self.safe_balance = safe_balance
        self.total_balance = total_balance

"""
export interface CulturelandCharge {
    /**
     * 성공 여부 메시지
     */
    message: "충전 완료" | "상품권지갑 보관" | "잔액이 0원인 상품권" | "상품권 번호 불일치";
    /**
     * 충전 금액
     */
    amount: number;
}

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

export interface ChangeCoupangCashResponse {
    resultCd: str
    resultMsg: str
}

export interface CulturelandChangeCoupangCash {
    /**
     * (전환 수수료 6%가 차감된) 전환된 금액
     */
    amount: number;
}

export interface ChangeSmileCashResponse {
    resultCd: str
    resultMsg: str
}

export interface CulturelandChangeSmileCash {
    /**
     * (전환 수수료 5%가 과금된) 과금된 금액
     */
    amount: number;
}

export interface CulturelandGooglePlay {
    /**
     * 기프트 코드 번호
     */
    pin: str
    /**
     * 자동 입력 URL
     */
    url: str
    /**
     * 카드번호
     */
    certNo: str
}

export interface GooglePlayBuyResponse {
    errCd: str
    pinBuyYn: Literal["Y", "N"]
    errMsg: str
}

export interface GooglePlayHistoryResponse {
    list: {
        item: {
            fee: str
            reSendState: Literal["Y", "N"]
            cnclState: Literal["Y", "N"]
            strLevyDate: str
            CertGroup: str
            ContentsName: str
            PurchaseCertNo: str
            LevyTime: str
            strMaskScrachNo: str
            payType: "컬쳐캐쉬" | "신용카드";
            strRcvInfo: str
            ReceiveInfo: str
            culturelandGiftNo: str
            ReSend: str
            culturelandGiftMaskNo: str
            ExSubMemberCode: str
            certGroup: str
            FaceValue: str
            strLevyTime: str
            levyDateTime: str
            ContentsCode: "GOOGLE";
            Amount: str
            ControlCode: str
            PinSaleControlCode: str
            cultureGiftFaceValue: str
            RowNumber: str
            CouponCode: str
            GCSubMemberCode: str
            CancelDate: str
            ExMemberCode: str
            State: str
            SubMemberCode: str
            googleDcUserHpCheck: Literal["Y", "N"]
            MemberControlCode: str
            CertNo: str
            ScrachNo: str
            LevyDate: str
            cnclLmtDate: str
        }
    }[];
    cpnVO: {
        buyType: null,
        cpgm: null;
        couponNm: null;
        contentsCd: null;
        alertAmt: null;
        couponAmt: null;
        saleAmt: null;
        comments: null;
        agreeMsg: null;
        serviceStatus: null;
        tfsSeq: null;
        hpNo1: null;
        hpNo2: null;
        hpNo3: null;
        recvHP: null;
        email1: null;
        email2: null;
        recvEmail: null;
        sendType: null;
        buyCoupon: null;
        direction: null;
        couponCode: null;
        memberCd: null;
        pinType: null;
        agencyNm: null;
        faceval: null;
        safeBalance: null;
        hp_no1: null;
        hp_no2: null;
        hp_no3: null;
        phoneNumber: null;
        prodNo: null;
        tmpCLState: null;
        res_code: null;
        datasize: null;
        salePercent: null;
        saleBuyLimit: null;
        isSale: 0;
        balance: 0;
        safeAmt: 0;
        amount: 0;
        arrCouponAmt: null;
        arrSaleAmt: null;
        arrSalePer: null;
        arrBuyCoupon: null;
        arrAlertAmt: null;
        arrCouponCode: null;
        arrCouponName: null;
        arrComments: null;
        couponCodeType: null;
        remainMAmount: null;
        remainDAmount: null;
        remainMAmountUser: null;
        remainDAmountUser: null;
        maxMAmountUser: null;
        maxDAmountUser: null;
        feeType: null;
        quantity: 0;
        page: number;
        pageSize: number;
        buyCnt: number;
        totalCnt: number;
        feeAmount: 0;
        fee: "0";
        isLastPageYn: Literal["Y", "N"]
        controlCd: null;
        subMemberCd: null;
        pinSaleControlCd: null;
        recvInfo: null;
        code1: null;
        code2: null;
        code3: null;
        code4: null;
        code5: null;
        recvType: null;
        couponContent: null;
        oriAmount: null;
        isCulSale: 0;
        deliveryFee: 0;
        deliveryType: "";
        recvNm: "";
        recvPost: "";
        recvAddr1: "";
        recvAddr2: "";
        envelopeQty: 0;
        billCheck: "";
        isEvnFee: 0;
        evnFee: "0";
        evnFeeAmount: 0;
        freefeeAmount: 0;
        eventCode: null;
        cpnType: "";
        salePer: null;
    }
}

export interface UserInfoResponse {
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
    size: number;
    user_id: str
    succUrl: str
    userIp: str
    Mobile_Yn: Literal["Y", "N"]
    idx: str
    category: str
}

export interface CulturelandUser {
    /**
     * 휴대폰 번호
     */
    phone: str
    /**
     * 안심금고 레벨
     */
    safeLevel: number;
    /**
     * 안심금고 비밀번호 여부
     */
    safePassword: boolean;
    /**
     * 가입 시각
     */
    registerDate: number;
    /**
     * 컬쳐랜드 ID
     */
    userId: str
    /**
     * 유저 고유 번호
     */
    userKey: str
    /**
     * 접속 IP
     */
    userIp: str
    /**
     * 유저 고유 인덱스
     */
    index: number;
    /**
     * 유저 종류
     */
    category: str
}

export interface CulturelandMember {
    /**
     * 컬쳐랜드 ID
     */
    id?: str
    /**
     * 멤버의 이름 | `홍*동`
     */
    name?: str
    /**
     * 멤버의 인증 등급
     */
    verificationLevel?: "본인인증";
}

export type CashLogsResponse = {
    item: {
        accDate: string,
        memberCode: string,
        outAmount: string,
        balance: string,
        inAmount: string,
        NUM: string,
        Note: string,
        accTime: string,
        memberName: string,
        accType: string,
        safeAmount: string
    }
}[];

export interface CulturelandCashLog {
    /**
     * 내역 제목
     */
    title: string,
    /**
     * 사용 가맹점 코드
     */
    merchantCode: string,
    /**
     * 사용 가맹점 이름
     */
    merchantName: string,
    /**
     * 사용 금액
     */
    amount: number,
    /**
     * 사용 후 남은 잔액
     */
    balance: number,
    /**
     * 사용 종류
     */
    spendType: "사용" | "사용취소" | "충전",
    /**
     * 사용 시각
     */
    timestamp: number
};

export interface CulturelandLogin {
    /**
     * 컬쳐랜드 ID
     */
    userId: str
    /**
     * 로그인 유지 쿠키
     */
    keepLoginConfig: str
}"""