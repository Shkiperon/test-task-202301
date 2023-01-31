from asterisk.ami import AMIClient, Action, FutureResponse
from asterisk.ami.event import EventListener, Event
from uuid import UUID
from typing import Optional
from datetime import datetime
import logging

from settings import AMI_CONN, AMI_CREDS, trunk_name
from mysql_connector.queries import MysqlQueries


class AsteriskListener():
    client: AMIClient

    def __init__(self):
        self._dict_calls = {}
        self.client = AMIClient(**AMI_CONN)
        self.client.login(**AMI_CREDS)
        self.client.add_event_listener(self._event_listener)
    
    def _event_listener(self, event: Event, **kwargs):
        print(f'[{datetime.now()}]: {event.name} - {event.keys}')
        if event.name == 'VarSet' and event.keys['Variable'] == 'call_id':
            logging.info(f'{datetime.now()}')
            self._dict_calls[event.keys['Linkedid']] = event.keys['Value']
        elif event.name == 'DialBegin':
            logging.info(f'{datetime.now()}')
            self._started = True
            sql = MysqlQueries()
            if not sql.upd_timefield_of_call(self._dict_calls[event.keys['DestLinkedid']], 'call_started'):
                logging.error(f'Unable to save datetime when call_id {self._dict_calls[event.keys["DestLinkedid"]]} started (linked_id {event.keys["DestLinkedid"]})')
            del sql
        elif event.name == 'DialEnd':
            logging.info(f'{datetime.now()}')
            self._answered = True
            sql = MysqlQueries()
            if not sql.upd_timefield_of_call(self._dict_calls[event.keys['Linkedid']], 'call_answered'):
                logging.error(f'Unable to save datetime when call_id {self._dict_calls[event.keys["Linkedid"]]} POSSIBLY answered (linked_id {event.keys["Linkedid"]})')
            del sql
        #TODO Fix problem with non-detected Hangups
        elif event.name == 'Hangup':
            logging.info(f'{datetime.now()}')
            self._hanguped = True
            sql = MysqlQueries()
            if not sql.upd_mark_call_as_finished(self._dict_calls[event.keys['Linkedid']], event.keys['Cause-txt']):
                logging.error(f'Unable to save datetime when call_id {self._dict_calls[event.keys["Linkedid"]]} finished (linked_id {event.keys["Linkedid"]})')
            del sql
            del self._dict_calls[event.keys["Linkedid"]]

class AsteriskCTL():
    client: AMIClient
    _call_id: int
    _task_id: UUID

    def __init__(self, call_id: int, task_id: UUID):
        self.client = AMIClient(**AMI_CONN)
        self._call_id = call_id
        self._task_id = task_id
        
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
        ami_response = self.client.send_action(action=ami_action)
        self.client.logoff()
        return ami_response.response

