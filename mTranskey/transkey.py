import math
import os
import random
import re
import time
import httpx

from typing import Literal
from .keypad import Keypad
from .rsa import CULTURELAND_PUBLICKEY, rsa_encrypt

class mTranskey:
    def __init__(self, client: httpx.Client):
        self.client = client
        self.transkey_uuid = os.urandom(32).hex()
        self.gen_session_key = os.urandom(8).hex()
        self.session_key = [int(self.gen_session_key[i], 16) for i in range(16)]
        self.encrypted_session_key = rsa_encrypt(self.gen_session_key, CULTURELAND_PUBLICKEY)
        self.allocation_index = random.SystemRandom().randrange(2 ** 32 - 1)

    def get_servlet_data(self):
        """
        트랜스키 서블릿 정보를 받아옵니다.

        반환값: {
            "request_token": `TK_requestToken`,
            "init_time": `initTime`,
            "key_info": [
                `qwerty 키보드 키 좌표`,
                `숫자 키보드 키 좌표`
            ]
        }
        """

        # TK_requestToken
        request_token_response = self.client.get("https://m.cultureland.co.kr/transkeyServlet?op=getToken&" + str(math.floor(time.time() * 1000)))
        request_token_regex = re.compile("var TK_requestToken=([\\d-]+);")
        request_token_match = request_token_regex.search(request_token_response.text)
        request_token = request_token_match[1] if request_token_match else "0"

        # initTime
        init_time_response = self.client.get("https://m.cultureland.co.kr/transkeyServlet?op=getInitTime")
        init_time_regex = re.compile("var initTime='([\\d-]+)';")
        init_time_match = init_time_regex.search(init_time_response.text)
        init_time = init_time_match[1] if init_time_match else "0"

        # keyInfo (키 좌표)
        key_positions_response = self.client.post(
            "https://m.cultureland.co.kr/transkeyServlet",
            data={
                "op": "getKeyInfo",
                "key": self.encrypted_session_key,
                "transkeyUuid": self.transkey_uuid,
                "useCert": "true",
                "TK_requestToken": request_token,
                "mode": "Mobile"
            }
        )

        [qwerty, number] = key_positions_response.text.split("var numberMobile = new Array();")
        points_regex = re.compile("key\\.addPoint\\((\\d+), (\\d+)\\);")

        # keyInfo.qwerty
        qwerty_info = []
        qwerty_points = qwerty.split("qwertyMobile.push(key);")
        qwerty_points.pop()

        for p in qwerty_points:
            points = points_regex.findall(p)
            key = points[0]
            qwerty_info.append([int(key[0]), int(key[1])]) # 키 좌표

        # keyInfo.number
        number_info = []
        number_points = number.split("numberMobile.push(key);")
        number_points.pop()

        for p in number_points:
            points = points_regex.findall(p)
            key = points[0]
            number_info.append([int(key[0]), int(key[1])]) # 키 좌표

        return {
            "request_token": request_token,
            "init_time": init_time,
            "key_info": [
                qwerty_info,
                number_info
            ]
        }

    def create_keypad(self, servlet_data, keyboard_type: Literal["qwerty", "number"], name: str, input_name: str, field_type = "password"):
        """
        트랜스키 서블릿 정보를 바탕으로 키패드를 생성합니다.

        파라미터:
            * servlet_data: 트랜스키 서블릿 정보 `TK_requestToken` `initTime` `키 좌표`
            * keyboard_type: 키보드 종류 (`qwerty` | `number`)
            * name: 키패드 아이디 (`txtScr14`)
            * input_name: 키패드 이름 (`scr14`)
            * field_type: 키패드 종류 (`password`)

        반환값:
            Keypad
        """

        return Keypad(
            {
                "transkey_uuid": self.transkey_uuid,
                "gen_session_key": self.gen_session_key,
                "session_key": self.session_key,
                "encrypted_session_key": self.encrypted_session_key,
                "allocation_index": self.allocation_index
            },
            servlet_data,
            self.client,
            keyboard_type,
            name,
            input_name,
            field_type
        )
