import os
from flask.views import MethodView
from flask import request
from uuid import uuid4, UUID

from settings import UPLOAD_FOLDER
from task_processor.models import allowed_file, ResponseTaskProcessor, \
    ParseFileAndSaveToDB, StopTaskWithCalls


class TaskProcessor(MethodView):
    def post(self):
        http_response = ResponseTaskProcessor()
        if 'file' not in request.files:
            http_response.error.code = 'NO_FILE_IN_REQUEST'
            return http_response.toResponse(400)
        file = request.files['file']
        filename = str(file.filename)
        if filename == '':
            http_response.error.code = 'NO_FILE_SELECTED'
            return http_response.toResponse(400)
        if file and allowed_file(filename):
            task_id = uuid4()
            target_full_filepath = os.path.join(UPLOAD_FOLDER, f"{task_id}.{filename.rsplit('.', 1)[1].lower()}")
            file.save(target_full_filepath)
            parser = ParseFileAndSaveToDB(target_full_filepath)
            if not parser.parse_file():
                http_response.error.code = 'PARSER_ERROR'
                http_response.error.message = parser.err_message
                return http_response.toResponse(400)
            if not parser.save_task_to_db(task_id):
                http_response.error.code = 'DATABASE_ERROR'
                http_response.error.message = parser.err_message
                return http_response.toResponse(500)
            http_response.success = True
            http_response.task_id = str(task_id)
            return http_response.toResponse(201)
        http_response.error.code = 'BAD_FILE_EXTENSION'
        http_response.error.message = 'Only csv and txt files allowed'
        return http_response.toResponse(400)

    def delete(self, task_id: UUID):
        http_response = ResponseTaskProcessor()
        http_response.task_id = str(task_id)
        stopper = StopTaskWithCalls(task_id)
        if stopper.do():
            http_response.success = True
            return http_response.toResponse(200)
        http_response.error.message = stopper.err_message
        if stopper.err_message is not None and stopper.err_message[0:5] != 'Task ':
            http_response.error.code = 'LOGIC_ERROR'
            return http_response.toResponse(400)
        http_response.error.code = 'DATABASE_ERROR'
        return http_response.toResponse(500)

