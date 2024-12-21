import hashlib
import hmac
import httpx

from typing import Literal
from io import BytesIO
from PIL import Image
from .seed import Seed

SPECIAL_CHARS = ["`", "~", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "_", "=", "+", "[", "{", "]", "}", "\\", "|", ";", ":", "/", "?", ",", "<", ".", ">", "'", "\"", "+", "-", "*", "/"]
LOWER_CHARS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "a", "s", "d", "f", "g", "h", "j", "k", "l", "z", "x", "c", "v", "b", "n", "m"]
NUMBER_KEY_HASHES = [
    "ddab8c8a364fc679c3356634e08bbb3a", # 0
    "e5e0c69c0773cd04fa3726c048070a2d", # 1
    "f5ad1500010a17d21b5d745f11e8f416", # 2
    "272e10c9cd3e03edad4597395566c22f", # 3
    "defc5b165f4f2c117e8b551a81b57d84", # 4
    "1e2d32fd1d66cddb4d819c03bf352e58", # 5
    "37a14c6662f520503836d26fbe9ba8fe", # 6
    "fa7a03f89600078030a8a930cd8cc0ad", # 7
    "0ae13319f6139af10cbcca5fd8fa7a47", # 8
    "da4d4c4be55781ce54f88e1f5550e72d", # 9
    "6fc0f70702615ba21a5cdd09ec45c3a0" # empty
]
BLANK_KEY_HASH = "" # qwerty 키보드 빈칸

class Keypad:
    def __init__(self, transkey_data: dict, servlet_data: dict, client: httpx.Client, keyboard_type: Literal["qwerty", "number"], name: str, input_name: str, field_type: str):
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
            * pw: 비밀번호
            * layout: 키패드 배열

        반환값:
            (암호화된 비밀번호, 암호화된 비밀번호의 HMAC 해시값)
        """

        encrypted = ""

        for val in pw:
            key_info = self.servlet_data.get("key_info")
            if self.keyboard_type == "qwerty":
                keyboard = key_info[0]
            else:
                keyboard = key_info[1]

            keyboard_index = layout.index(
                SPECIAL_CHARS.index(val) if val in SPECIAL_CHARS # val이 특수문자라면 특수문자 키보드에서 val의 위치
                else LOWER_CHARS.index(val.lower()) if self.keyboard_type == "qwerty" # qwerty 키보드라면 qwerty 키보드에서 val의 위치
                else int(val) # 숫자 키보드에서 val의 위치
            )

            try:
                geo = keyboard[keyboard_index]
            except (IndexError, ValueError):
                raise Exception("입력할 수 없는 키가 입력되었습니다.") # 키패드에 존재하지 않는 키

            geo = list(map(str, geo))
            if self.keyboard_type == "qwerty": # qwerty 키보드라면
                if val in SPECIAL_CHARS: # 특수문자라면
                    geo_string = "s " + " ".join(geo)
                elif val == val.upper(): # 대문자라면
                    geo_string = "u " + " ".join(geo)
                else: # 소문자 또는 숫자라면
                    geo_string = "l " + " ".join(geo)
            else: # 숫자 키보드라면
                geo_string = " ".join(geo)

            encrypted += "$" + Seed.SeedEnc(geo_string, self.transkey_data.get("session_key"))

        encrypted_hmac = hmac.new(
            msg=encrypted.encode(),
            key=self.transkey_data.get("gen_session_key").encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

        return (encrypted, encrypted_hmac)

    def get_keypad_layout(self):
        """
        키패드 사진을 분석하여 키패드 배열을 가져옵니다.

        반환값:
            키패드 배열
        """

        key_index_request = self.client.post(
            "https://m.cultureland.co.kr/transkeyServlet",
            data={
                "op": "getKeyIndex",
                "name": self.name,
                "keyType": "lower" if self.keyboard_type == "qwerty" else "single",
                "keyboardType": self.keyboard_type + "Mobile",
                "fieldType": self.field_type,
                "inputName": self.input_name,
                "parentKeyboard": "false",
                "transkeyUuid": self.transkey_data.get("transkey_uuid"),
                "exE2E": "false",
                "TK_requestToken": self.servlet_data.get("request_token"),
                "allocationIndex": self.transkey_data.get("allocation_index"),
                "keyIndex": self.key_index,
                "initTime": self.servlet_data.get("init_time"),
                "talkBack": "true"
            }
        )
        self.key_index = key_index_request.text

        key_image_response = self.client.get(
            "https://m.cultureland.co.kr/transkeyServlet",
            params={
                "op": "getKey",
                "name": self.name,
                "keyType": "lower" if self.keyboard_type == "qwerty" else "single",
                "keyboardType": self.keyboard_type + "Mobile",
                "fieldType": self.field_type,
                "inputName": self.input_name,
                "parentKeyboard": "false",
                "transkeyUuid": self.transkey_data.get("transkey_uuid"),
                "exE2E": "false",
                "TK_requestToken": self.servlet_data.get("request_token"),
                "allocationIndex": self.transkey_data.get("allocation_index"),
                "keyIndex": self.key_index,
                "initTime": self.servlet_data.get("init_time")
            }
        )

        key_image = Image.open(BytesIO(key_image_response.content))
        keys: list[Image.Image] = []

        for y in range(4 if self.keyboard_type == "qwerty" else 3): # 키패드 세로 칸만큼 반복
            for x in range(11 if self.keyboard_type == "qwerty" else 4): # 키패드 가로 칸만큼 반복
                if self.keyboard_type == "qwerty": # qwerty 키보드라면
                    if (x == 0 and y == 3) or ((x == 9 or x == 10) and y == 3): # shift or backspace
                        continue # 불필요한 키는 건너뛰기

                img = key_image.crop([
                    x * 54 + 22 if self.keyboard_type == "qwerty" else x * 160 + 70, # 시작점 x 좌표
                    y * 80 + 30 if self.keyboard_type == "qwerty" else y * 102 + 45, # 시작점 y 좌표
                    x * 54 + 37 if self.keyboard_type == "qwerty" else x * 160 + 90, # 끝점 x 좌표
                    y * 80 + 75 if self.keyboard_type == "qwerty" else y * 102 + 70 # 끝점 y 좌표
                ]) # 키패드 칸의 중앙만 남게 사진을 잘라냄

                keys.append(img)

        layout = []
        i = 0
        for key in keys:
            key_img_bytes = BytesIO()
            key.save(key_img_bytes, "PNG")
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
