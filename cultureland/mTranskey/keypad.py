import hashlib
import hmac
import httpx

from typing import Literal
from io import BytesIO
from PIL import Image
from .seed import Seed
from ._types import TranskeyData, ServletData

SPECIAL_CHARS = ["`", "~", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "_", "=", "+", "[", "{", "]", "}", "\\", "|", ";", ":", "/", "?", ",", "<", ".", ">", "'", "\"", "+", "-", "*", "/"]
LOWER_CHARS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "a", "s", "d", "f", "g", "h", "j", "k", "l", "z", "x", "c", "v", "b", "n", "m"]
NUMBER_KEY_HASHES = [
    "239a38c2463e82430120570e0a71b0b6", # 0
    "0246598c40a2ceba0afb34b7e256bb3d", # 1
    "807ca18d6f1f454b82edad0733ab5039", # 2
    "4b785ee9fd589e68997927e8734d9a48", # 3
    "dabe316ee795a0aa9866878716330998", # 4
    "248e70819a775b669371728f391d0220", # 5
    "5bbfd356baf3830f97803642e8c6693f", # 6
    "1513dd2b504c53c764f3fde5dd9aa5f6", # 7
    "c6845589018515678077282a75b796dd", # 8
    "ea784a29bfd1f17276320d6148ba67f8", # 9
    "9c36f62dca0fe9b2174f5129f2a44283" # empty
]
BLANK_KEY_HASH = "be2e2eb24d35ec52b7205dc1b8d78b08" # qwerty 키패드 빈칸

class Keypad:
    def __init__(self, transkey_data: TranskeyData, servlet_data: ServletData, client: httpx.AsyncClient, keyboard_type: Literal["qwerty", "number"], name: str, input_name: str, field_type: str):
        self.transkey_data = transkey_data
        self.servlet_data = servlet_data
        self.client = client
        self.keyboard_type = keyboard_type
        self.name = name
        self.input_name = input_name
        self.field_type = field_type
        self.key_index = ""

    def encrypt_password(self, pw: str, layout: list[int]):
        """
        비밀번호를 키패드 배열에 따라 암호화합니다.

        파라미터:
            * pw (str): 비밀번호
            * layout (list[int]): 키패드 배열

        반환값:
            (암호화된 비밀번호, 암호화된 비밀번호의 HMAC 해시값)
        """

        encrypted = ""

        for val in pw:
            if self.keyboard_type == "qwerty":
                keyboard = self.servlet_data.qwerty_info
            else:
                keyboard = self.servlet_data.number_info

            keyboard_index = layout.index(
                SPECIAL_CHARS.index(val) if val in SPECIAL_CHARS # val이 특수문자라면 특수문자 키패드에서 val의 위치
                else LOWER_CHARS.index(val.lower()) if self.keyboard_type == "qwerty" # qwerty 키패드라면 qwerty 키패드에서 val의 위치
                else int(val) # 숫자 키패드에서 val의 위치
            )

            try:
                geo = keyboard[keyboard_index]
            except (IndexError, ValueError):
                raise Exception("입력할 수 없는 키가 입력되었습니다.") # 키패드에 존재하지 않는 키

            geo = list(map(str, geo))
            if self.keyboard_type == "qwerty": # qwerty 키패드라면
                if val in SPECIAL_CHARS: # 특수문자라면
                    geo_string = "s " + " ".join(geo)
                elif val == val.upper(): # 대문자라면
                    geo_string = "u " + " ".join(geo)
                else: # 소문자 또는 숫자라면
                    geo_string = "l " + " ".join(geo)
            else: # 숫자 키패드라면
                geo_string = " ".join(geo)

            encrypted += "$" + Seed.SeedEnc(geo_string, self.transkey_data.get_session_key())

        encrypted_hmac = hmac.new(
            msg=encrypted.encode(),
            key=self.transkey_data.generated_session_key.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

        return (encrypted, encrypted_hmac)

    async def get_keypad_layout(self):
        """
        키패드 사진을 분석하여 키패드 배열을 가져옵니다.

        반환값:
            키패드 배열
        """

        key_index_request = await self.client.post(
            "/transkeyServlet",
            data={
                "op": "getKeyIndex",
                "name": self.name,
                "keyType": "lower" if self.keyboard_type == "qwerty" else "single",
                "keyboardType": self.keyboard_type + "Mobile",
                "fieldType": self.field_type,
                "inputName": self.input_name,
                "parentKeyboard": "false",
                "transkeyUuid": self.transkey_data.transkey_uuid,
                "exE2E": "false",
                "TK_requestToken": self.servlet_data.request_token,
                "allocationIndex": self.transkey_data.allocation_index,
                "keyIndex": self.key_index,
                "initTime": self.servlet_data.init_time,
                "talkBack": "true"
            }
        )
        self.key_index = key_index_request.text

        key_image_response = await self.client.get(
            "/transkeyServlet",
            params={
                "op": "getKey",
                "name": self.name,
                "keyType": "lower" if self.keyboard_type == "qwerty" else "single",
                "keyboardType": self.keyboard_type + "Mobile",
                "fieldType": self.field_type,
                "inputName": self.input_name,
                "parentKeyboard": "false",
                "transkeyUuid": self.transkey_data.transkey_uuid,
                "exE2E": "false",
                "TK_requestToken": self.servlet_data.request_token,
                "allocationIndex": self.transkey_data.allocation_index,
                "keyIndex": self.key_index,
                "initTime": self.servlet_data.init_time
            }
        )

        key_image = Image.open(BytesIO(key_image_response.content))
        keys: list[Image.Image] = []

        for y in range(4 if self.keyboard_type == "qwerty" else 3): # 키패드 세로 칸만큼 반복
            for x in range(11 if self.keyboard_type == "qwerty" else 4): # 키패드 가로 칸만큼 반복
                if self.keyboard_type == "qwerty": # qwerty 키패드라면
                    if (x == 0 and y == 3) or ((x == 9 or x == 10) and y == 3): # shift or backspace
                        continue # 불필요한 키는 건너뛰기

                img = key_image.crop([
                    x * 54 + 22 if self.keyboard_type == "qwerty" else x * 160 + 70, # 시작점 x 좌표
                    y * 80 + 30 if self.keyboard_type == "qwerty" else y * 102 + 45, # 시작점 y 좌표
                    x * 54 + 37 if self.keyboard_type == "qwerty" else x * 160 + 90, # 끝점 x 좌표
                    y * 80 + 75 if self.keyboard_type == "qwerty" else y * 102 + 70 # 끝점 y 좌표
                ]) # 키패드 칸의 중앙만 남게 사진을 잘라냄

                keys.append(img)

        layout: list[int] = []
        i = 0
        for key in keys:
            key_img_bytes = BytesIO()
            key.save(key_img_bytes, "BMP")
            key_payload = key_img_bytes.getvalue()

            enc = hashlib.md5()
            enc.update(key_payload)
            key_hash = enc.hexdigest() # 키 사진의 해시

            if self.keyboard_type == "qwerty":
                if key_hash == BLANK_KEY_HASH:
                    layout.append(-1) # 빈 칸
                else:
                    layout.append(i)
                    i += 1
            else:
                layout.append(NUMBER_KEY_HASHES.index(key_hash)) # 사진의 해시를 이용해 어떤 키인지 찾아냄

        return layout
