from asterisk.ami import AMIClient, Action, FutureResponse
from asterisk.ami.event import Event
from uuid import UUID
from typing import Optional
from datetime import datetime

from settings import AMI_CONN, AMI_CREDS, trunk_name
from mysql_connector.queries import MysqlQueries


class AsteriskCTL():
    client: AMIClient
    _call_id: int
    _task_id: UUID
    _call_linkedid: Optional[str]
    _started: bool
    _answered: bool
    _hanguped: bool

    def __init__(self, call_id: int, task_id: UUID):
        self.client = AMIClient(**AMI_CONN)
        self._call_id = call_id
        self._task_id = task_id
        self._call_linkedid = None
        self._started = False
        self._answered = False
        self._hanguped = False

    def _callback_response(self, response: FutureResponse):
        print(response)

    def _event_listener(self, event: Event, **kwargs):
        if event.name == 'VarSet' and event.keys['Variable'] == 'call_id' and event.keys['Value'] == str(self._call_id) and self._call_linkedid is None:
            print(f'{datetime.now()}')
            self._call_linkedid = event.keys['Linkedid']
        elif event.name == 'DialBegin' and event.keys['DestLinkedid'] == self._call_linkedid and not self._started:
            print(f'{datetime.now()}')
            self._started = True
            sql = MysqlQueries()
            if not sql.upd_timefield_of_call(self._call_id, 'call_started'):
                print(f'Unable to save datetime when call_id {self._call_id} started (linked_id {self._call_linkedid})')
            del sql
        elif event.name == 'DialEnd' and event.keys['Linkedid'] == self._call_linkedid and not self._answered:
            print(f'{datetime.now()}')
            self._answered = True
            sql = MysqlQueries()
            if not sql.upd_timefield_of_call(self._call_id, 'call_answered'):
                print(f'Unable to save datetime when call_id {self._call_id} POSSIBLY answered (linked_id {self._call_linkedid})')
            del sql
        #TODO Fix problem with non-detected Hangups
        elif event.name == 'Hangup' and event.keys['Linkedid'] == self._call_linkedid and not self._hanguped:
            print(f'{datetime.now()}')
            self._hanguped = True
            sql = MysqlQueries()
            if not sql.upd_mark_call_as_finished(self._call_id, event.keys['Cause-txt']):
                print(f'Unable to save datetime when call_id {self._call_id} finished (linked_id {self._call_linkedid})')
            del sql
            self.client.logoff()

    def make_call(self, name:str, number: int) -> FutureResponse:
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
                'call_id': self._call_id,
                'task_id': self._task_id
            }
        )
        self.client.add_event_listener(self._event_listener)
        ami_response = self.client.send_action(action=ami_action, callback=self._callback_response)
        return ami_response.response

