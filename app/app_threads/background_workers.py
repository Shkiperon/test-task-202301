import logging
from threading import Thread
from time import sleep
from queue import Queue
from uuid import UUID

from mysql_connector.queries import MysqlQueries
from ami_connector.engine import AsteriskCTL


class FillQueueWorker(Thread):
    _queue: Queue

    def __init__(self, queue: Queue):
        Thread.__init__(self)
        self._queue = queue

    def run(self):
        while True:
            if not self._queue.full():
                sql1 = MysqlQueries()
                sql2 = MysqlQueries()
                try:
                    if sql1.sel_idle_call_id() and sql1.result is not None:
                        if sql2.upd_take_idle_call_id(int(sql1.result['call_id'])):
                            #Structure of sql1.result:
                            #{
                            #  'call_id': int,
                            #  'task_id': UUID in string format,
                            #  'call_number': int,
                            #  'call_name': str
                            #}
                            self._queue.put(sql1.result)
                except Exception as ex:
                    logging.error(f'Error in FillQueueWorker loop - "{ex}"')
                del sql1
                del sql2
            sleep(0.5)


class CallWorker(Thread):
    _queue: Queue

    def __init__(self, queue: Queue):
        Thread.__init__(self)
        self._queue = queue

    def run(self):
        while True:
            if not self._queue.empty():
                #Structure of call_task_dict:
                #{
                #  'call_id': int,
                #  'task_id': UUID in string format,
                #  'call_number': int,
                #  'call_name': str
                #}
                call_task_dict = self._queue.get()
                try:
                    ami_worker = AsteriskCTL(int(call_task_dict['call_id']), UUID(call_task_dict['task_id']))
                    ami_worker.make_call(str(call_task_dict['call_name']), int(call_task_dict['call_number']))
                    del ami_worker
                except Exception as ex:
                    logging.error(f'Error in CallWorker loop - "{ex}"')
                finally:
                    self._queue.task_done()
            sleep(0.5)

