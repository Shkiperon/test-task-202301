from flask import Response
from typing import Optional
import json
import re
from uuid import UUID

from settings import ALLOWED_EXTENSIONS
from mysql_connector.queries import MysqlQueries

def allowed_file(filename: str):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class ParseFileAndSaveToDB():
    _filepath: str
    err_message: Optional[str]
    task_elements: dict

    def __init__(self, full_filepath: str):
        self._filepath = full_filepath
        self.task_elements = {}
        
    def parse_file(self) -> bool:
        self.err_message = None
        file = open(self._filepath, 'r')
        list_numbers = []
        for line in file:
            if line == '':
                continue
            line_match = re.match(r'^(\w+);(\d+)$', line)
            if line_match is not None:
                self.task_elements[line_match.group(2)] = line_match.group(1)
                list_numbers.append(line_match.group(2))
            else:
                self.err_message = 'Incorrect lines founded in file. Processing stopped'
                return False
        if len(self.task_elements.keys()) == len(list_numbers):
            return True
        else:
            self.err_message = 'Some duplicates founded in file. Check the file and try again'
            return False

    def save_task_to_db(self, task_id: UUID) -> bool:
        self.err_message = None
        sql = MysqlQueries()
        if sql.ins_new_task(task_id):
            for call_number, call_name in self.task_elements.items():
                if not sql.ins_task_element(task_id, call_number, call_name):
                    self.err_message = sql.err_info
                    return False
        else:
            self.err_message = sql.err_info
            return False
        return True


class StopTaskWithCalls():
    task_id: UUID
    err_message: Optional[str]

    def __init__(self, task_id: UUID):
        self.task_id = task_id
        self.err_message = None

    def do(self) -> bool:
        sql = MysqlQueries()
        if sql.upd_mark_stop_calls(self.task_id):
            if sql.upd_mark_stop_task(self.task_id):
                #Task and unstarted calls marked as manually stopped
                return True
            elif sql.err_info != 'affected 0 rows':
                self.err_message = sql.err_info
            else:
                self.err_message = 'Task was already marked as stopped but some unstarted calls has been marked as manually stopped'
        else:
            if sql.err_info != 'affected 0 rows':
                self.err_message = sql.err_info
            else:
                if sql.upd_mark_stop_task(self.task_id):
                    self.err_message = 'Task marked as stopped but there are no unstarted calls left'
                elif sql.err_info != 'affected 0 rows':
                    self.err_message = sql.err_info
                else:
                    self.err_message = 'Task was already marked as stopped'
        return False


class ResponseError():
    code: Optional[str]
    message: Optional[str]

    def __init__(self, err_type: Optional[str] = None, err_message: Optional[str] = None):
        self.code = err_type
        self.message = err_message


class ResponseTaskProcessor():
    success: bool
    task_id: Optional[str]
    error: ResponseError

    def __init__(self):
        self.success = False
        self.error = ResponseError()

    def toJson(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True
        )

    def toResponse(self, http_code: int = 200):
        return Response(self.toJson(), http_code, mimetype='application/json')

