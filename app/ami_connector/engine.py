from asterisk.ami import AMIClient

from settings import AMI_CONN, AMI_CREDS


class AsteriskCTL():
    __slots__ = [
        "client"
    ]

    def __init__(self):
        self.client = AMIClient(**AMI_CONN)

    def make_call(self, name:str, number: int, trunk_name: str):


