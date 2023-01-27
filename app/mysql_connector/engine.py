import mysql.connector as mysqlconn
from contextlib import closing
from typing import Optional, Any

from settings import MYSQL_CONN


class MysqlCTL():
    _config: dict
    success: bool
    result: Optional[Any]
    err_info: Optional[str]

    def __init__(self):
        self._config = MYSQL_CONN
        self.success = False
        self.result = None
        self.err_info = None

    def do_query(self, query: str, is_select: bool):
        try:
            with closing(mysqlconn.connect(**self._config)) as _connect:
                sql = _connect.cursor(dictionary=True)
                sql.execute(query)
                if is_select:
                    self.result = sql.fetchall()
                    self.success = True
                else:
                    _connect.commit()
                    affected_rows = sql.rowcount
                    if (affected_rows > 0):
                        self.success = True
                    else:
                        self.err_info = 'affected 0 rows'
                sql.close()
        except Exception as ex:
            self.err_info = f'SQL error\r\n{query}\r\n{ex}'.strip()

