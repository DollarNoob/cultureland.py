from .rsa import CULTURELAND_PUBLICKEY, rsa_encrypt

class TranskeyData:
    def __init__(self, transkey_uuid: str, generated_session_key: str, allocation_index: int):
        self.__transkey_uuid = transkey_uuid
        self.__generated_session_key = generated_session_key
        self.__allocation_index = allocation_index

    @property
    def transkey_uuid(self):
        """
        `transkeyUuid`
        """
        return self.__transkey_uuid

    @property
    def generated_session_key(self):
        """
        `genSessionKey`
        """
        return self.__generated_session_key

    @property
    def allocation_index(self):
        """
        `allocationIndex`
        """
        return self.__allocation_index

    def get_session_key(self):
        """
        `sessionKey`
        """
        return [int(self.__generated_session_key[i], 16) for i in range(16)]

    def get_encrypted_session_key(self):
        """
        `encSessionKey`
        """
        return rsa_encrypt(self.__generated_session_key, CULTURELAND_PUBLICKEY)

class ServletData:
    def __init__(self, request_token: str, init_time: str, qwerty_info: list[int], number_info: list[int]):
        self.__request_token = request_token
        self.__init_time = init_time
        self.__qwerty_info = qwerty_info
        self.__number_info = number_info

    @property
    def request_token(self):
        """
        `TK_requestToken`
        """
        return self.__request_token

    @property
    def init_time(self):
        """
        `initTime`
        """
        return self.__init_time

    @property
    def qwerty_info(self):
        """
        qwerty 키패드 키 좌표
        """
        return self.__qwerty_info

    @property
    def number_info(self):
        """
        숫자 키패드 키 좌표
        """
        return self.__number_info
