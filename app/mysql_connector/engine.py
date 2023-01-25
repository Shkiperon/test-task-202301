import mysql.connector as mysqlconn
from contextlib import closing

from settings import MYSQL_CONN


class MysqlCTL():
    __slots__ = [
        '_config',
        '_query_types',
        'result',
        'success',
        'err_info'
    ]

    def __init__(self):
        self._config = MYSQL_CONN
        self.result = None
        self.success = False
        self.err_info = None

    def _do_query(self, is_select: bool, query: str):
        try:
            with closing(mysqlconn.connect(**self._config)) as _connect:
                sql = _connect.cursor(dictionary=True)
                sql.execute(query)
                if is_select:
                    self.result = sql.fetchall()
                    self.success = True
                else:
                    _connect.commit()
                sql.close()
        except Exception as ex:
            self.err_info = f'SQL error\r\n{query}\r\n{ex}'.strip()
            print(self.err_info)

    def ins_new_task(self):
        pass

    def ins_task_element(self):
        pass

    def sel_idle_task_element(self):
        pass

    def upd_stop_task(self):
        #First query - mark unstarted task elements to skip execution
        #Second query - mark task as manually stopped at some datestamp
        pass

