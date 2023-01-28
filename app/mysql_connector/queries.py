from mysql_connector.engine import MysqlCTL
from uuid import UUID
from typing import Optional, Any


class MysqlQueries():
    result: Optional[Any]
    err_info: Optional[str]

    def __init__(self):
        pass

    def ins_new_task(self, task_id: UUID) -> bool:
        self.result = None
        self.err_info = None
        query = f"""
        INSERT INTO autocalls_tasks(task_id, task_created)
        VALUES ('{task_id}', NOW())
        """
        sql = MysqlCTL()
        sql.do_query(query, False)
        if sql.success:
            self.result = sql.result
        else:
            self.err_info = sql.err_info
        return sql.success

    def ins_task_element(self, task_id: UUID, call_number: int, call_name: str) -> bool:
        self.result = None
        self.err_info = None
        query = f"""
        INSERT INTO autocalls(task_id, call_created, call_number, call_name)
        VALUES ('{task_id}', NOW(), {call_number}, '{call_name}')
        """
        sql = MysqlCTL()
        sql.do_query(query, False)
        if sql.success:
            self.result = sql.result
        else:
            self.err_info = sql.err_info
        return sql.success

    def sel_idle_call_id(self) -> bool:
        self.result = None
        self.err_info = None
        query = f"""
        SELECT id as call_id, task_id, call_number, call_name
        FROM autocalls
        WHERE call_status IS NULL AND call_started IS NULL
        HAVING MIN(id)
        """
        sql = MysqlCTL()
        sql.do_query(query, True)
        if sql.success:
            self.result = sql.result
        else:
            self.err_info = sql.err_info
        return sql.success

    def upd_timefield_of_call(self, call_id: int, field_name: str):
        self.result = None
        self.err_info = None
        query = f"""
        UPDATE autocalls
        SET {field_name}=NOW()
        WHERE id={call_id} and {field_name} IS NULL
        """
        sql = MysqlCTL()
        sql.do_query(query, False)
        if sql.success:
            self.result = sql.result
        elif sql.err_info != 'affected 0 rows':
            self.err_info = sql.err_info
        return sql.success

    def upd_mark_call_as_finished(self, call_id: int, call_status: str):
        self.result = None
        self.err_info = None
        query = f"""
        UPDATE autocalls
        SET call_finished=NOW(), call_status='{call_status}'
        WHERE id={call_id} and call_finished IS NULL
        """
        sql = MysqlCTL()
        sql.do_query(query, False)
        if sql.success:
            self.result = sql.result
        elif sql.err_info != 'affected 0 rows':
            self.err_info = sql.err_info
        return sql.success

    def upd_mark_stop_calls(self, task_id: UUID) -> bool:
        self.result = None
        self.err_info = None
        query = f"""
        UPDATE autocalls
        SET call_status='TASK_STOPPED', call_finished=NOW()
        WHERE task_id={task_id} AND call_started IS NULL
        """
        sql = MysqlCTL()
        sql.do_query(query, False)
        if sql.success:
            self.result = sql.result
        elif sql.err_info != 'affected 0 rows':
            self.err_info = sql.err_info
        return sql.success

    def upd_mark_stop_task(self, task_id: UUID) -> bool:
        query = f"""
        UPDATE autocalls_tasks
        SET task_stopped=NOW()
        WHERE task_id={task_id}
        """
        sql = MysqlCTL()
        sql.do_query(query, False)
        if sql.success:
            self.result = sql.result
        elif sql.err_info != 'affected 0 rows':
            self.err_info = sql.err_info
        return sql.success

