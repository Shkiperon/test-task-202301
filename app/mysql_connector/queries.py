from mysql_connector.engine import MysqlCTL
from uuid import UUID


class MysqlQueries():
    __slots__ = [
        'result',
        'err_info'
    ]

    def __init__(self):
        self.result = None
        self.err_info = None


    def ins_new_task(self, task_id: UUID) -> bool:
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

    def upd_stop_task(self, task_id: UUID) -> bool:
        #First query - mark unstarted task elements to skip execution
        query1 = f"""
        UPDATE autocalls
        SET call_status='TASK_STOPPED', call_finished=NOW()
        WHERE task_id={task_id} AND call_started IS NULL
        """
        sql1 = MysqlCTL()
        sql1.do_query(query1, False)
        if not sql1.success and sql1.err_info != 'affected 0 rows':
            self.err_info = sql1.err_info
            return sql1.success
        #Second query - mark task as manually stopped at some datestamp
        query2 = f"""
        UPDATE autocalls_tasks
        SET task_stopped=NOW()
        WHERE task_id={task_id}
        """
        sql2 = MysqlCTL()
        sql2.do_query(query2, False)
        if not sql2.success and sql2.err_info != 'affected 0 rows':
            self.err_info = sql2.err_info
            return sql2.success
        elif not sql2.success:
            err_prefix = 'Task'
            if not sql1.success:
                err_prefix += ' and calls'
            self.err_info = '{err_prefix} is already stopped'
            return sql2.success
        else:
            if not sql1.success:
                self.err_info = 'Calls was already finished. Task marked as stopped'
                return sql1.success
        self.result = 'Task and unstarted calls marked as manually stopped'
        return sql2.success

