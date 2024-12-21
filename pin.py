import re
from typing import Union

class Pin:
    """
    핀번호를 관리하는 클래스입니다.
    핀번호 포맷팅에 사용됩니다.
    """

    def __init__(self, pin: Union[str, list[str]], *pin_parts: str):
        """
        핀번호를 자동으로 포맷팅합니다.
        핀번호가 유효하지 않은 경우 parts가 null을 반환합니다.

        파라미터:
            * pin: 상품권의 핀번호

        ```py
        # 올바른 핀번호일 경우:
        pin = Pin("3110-0123-4567-8901") # Pin("3110", "0123", "4567", "8901"), Pin(["3110", "0123", "4567", "8901"])
        print(pin.parts) # Output: ["3110", "0123", "4567", "8901"]

        # 올바르지 않은 핀번호일 경우:
        pin = Pin("swasd------") # CulturelandError [PinValidationError]: 존재하지 않는 상품권입니다.
        ```
        """

        if isinstance(pin, list):
            pin = "-".join(pin)
        elif len(pin_parts) == 3:
            pin = f"{pin}-{pin_parts[0]}-{pin_parts[1]}-{pin_parts[2]}"
        elif len(pin_parts) != 0:
            raise ValueError("존재하지 않는 상품권입니다.")

        validation_result = Pin.validate_client_side(pin)
        if not validation_result:
            raise ValueError("존재하지 않는 상품권입니다.")

        formatted = Pin.format(pin)
        if formatted is None:
            raise ValueError("존재하지 않는 상품권입니다.")

        self.__parts = formatted

    def __str__(self):
        """
        핀번호를 string으로 변환합니다.

        `"3110-0123-4567-8901"`
        """

        return "-".join(self.__parts)

    @property
    def parts(self):
        """
        포맷팅이 완료된 핀번호입니다.

        ```py
        pin = Pin("3110-0123-4567-8901")
        print(pin.parts) # ("3110", "0123", "4567", "8901")
        ```
        """

        return self.__parts

    @staticmethod
    def format(pin: str):
        """
        핀번호를 `tuple[str, str, str, str]` 형식으로 포맷팅합니다.

        `Pin.validate_client_side` 와 달리, 형식이 잘못된 상품권이 입력된 경우에 오류가 발생합니다.

        ```py
        Pin.format("3110-0123-4567-8901") # ("3110", "0123", "4567", "8901")
        Pin.format("3110-0123-4567-890123") # ("3110", "0123", "4567", "890123")
        Pin.format("3110-0123-4567-89012345") # ("3110", "0123", "4567", "890123")
        Pin.format("311000-0123-4567-8901") # ValueError: 존재하지 않는 상품권입니다.
        ```
        """

        pin_regex = re.compile("(\\d{4})\\D*(\\d{4})\\D*(\\d{4})\\D*(\\d{6}|\\d{4})")
        pin_matches: list[str] = pin_regex.findall(pin)
        if len(pin_matches) == 0:
            raise ValueError("존재하지 않는 상품권입니다.")

        pin_matches = pin_matches[0] # regex에 맞는 첫번째 핀번호

        parts = (pin_matches[0], pin_matches[1], pin_matches[2], pin_matches[3])
        return parts

    @staticmethod
    def validate_client_side(pin: str):
        """
        핀번호의 유효성을 검증합니다.

        존재할 수 없는 핀번호를 검사하여 불필요한 요청을 사전에 방지합니다.

        `Pin.format` 과 달리, 성공 여부만 bool로 반환하며 검증에 실패하더라도 오류가 발생하지 않습니다.

        파라미터:
            * pin (str): 상품권의 핀번호

        반환값:
            핀번호 유효 여부
        """

        pin_regex = re.compile("(\\d{4})\\D*(\\d{4})\\D*(\\d{4})\\D*(\\d{6}|\\d{4})")
        pin_matches = pin_regex.findall(pin) # 1111!@#!@#@#@!#!@#-1111-1111DSSASDA-1111와 같은 형식도 PASS됨.
        if len(pin_matches) == 0: # 핀번호 regex에 맞지 않는다면 검증 실패
            return False

        pin_matches = pin_matches[0] # regex에 맞는 첫번째 핀번호

        parts: tuple[str, str, str, str] = (pin_matches[0], pin_matches[1], pin_matches[2], pin_matches[3])
        if parts[0].startswith("416") or parts[0].startswith("4180"): # 핀번호가 416(컬쳐랜드상품권 구권) 또는 4180(컬쳐랜드상품권 신권)으로 시작한다면
            if len(parts[3]) != 4: # 마지막 핀번호 부분이 4자리가 아니라면 검증 실패
                return False
        elif parts[0].startswith("41"): # 핀번호가 41로 시작하지만 416 또는 4180으로 시작하지 않는다면 검증 실패
            return False
        elif parts[0].startswith("31") and parts[0][2] != "0" and len(parts[3]) == 4: # 핀번호가 31로 시작하고 3번째 자리가 1~9이고, 마지막 핀번호 부분이 4자리라면
            # 검증 성공 (2024년 3월에 추가된 핀번호 형식)
            # /assets/js/egovframework/com/cland/was/util/ClandCmmUtl.js L1281
            pass
        elif parts[0][0] in ["2", "3", "4", "5"]: # 핀번호가 2, 3, 4, 5로 시작한다면 (문화상품권, 온라인문화상품권)
            if len(parts[3]) != 6: # 마지막 핀번호 부분이 6자리가 아니라면 검증 실패
                return False
        else: # 위 조건에 하나도 맞지 않는다면 검증 실패
            return False

        return True
