from asterisk.ami import AMIClient, Action, FutureResponse
from uuid import UUID

from settings import AMI_CONN, AMI_CREDS


class AsteriskCTL():
    client: AMIClient

    def __init__(self):
        self.client = AMIClient(**AMI_CONN)

    def make_call(self, name:str, number: int, trunk_name: str, call_id: int, task_id: UUID) -> FutureResponse:
        self.client.login(**AMI_CREDS)
        ami_action = Action(
            name='Originate',
            keys={
                'Channel': 'Local/s@dialer-external',
                'Context': 'dialer-local',
                'Exten': 's',
                'Priority': 1,
                'CallerID': 'dialer'
            },
            variables={
                'name': name,
                'number': number,
                'trunk_name': trunk_name,
                'call_id': call_id,
                'task_id': task_id
            }
        )
        ami_response = self.client.send_action(ami_action)
        self.client.logoff()
        return ami_response.response

