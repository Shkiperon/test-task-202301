import os
from flask.views import MethodView
from flask import request
from werkzeug.utils import secure_filename

from task_processor.models import allowed_file, ResponseTaskProcessor
from application import app


class TaskProcessor(MethodView):
    def post(self):
        http_response = ResponseTaskProcessor()
        if 'file' not in request.files:
            http_response.error.code = 'NO_FILE_IN_REQUEST'
            return http_response.toResponse(400)
        file = request.files['file']
        if file.filename == '':
            http_response.error.code = 'NO_FILE_SELECTED'
            return http_response.toResponse(400)
        if file and allowed_file(str(file.filename)):
            filename = secure_filename(str(file.filename))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #TODO Add to models.py functions for processing the file (can return errors while processing)
            #and for start autocall proccess asynchronously.
            #After starting task - get info to API user about task number and the fact that autocall has benn started 
            http_response.success = True
            return http_response.toResponse(201)
        else:
            http_response.error.code = 'BAD_FILE_EXTENSION'
            http_response.error.message = 'Only csv and txt files allowed'
            return http_response.toResponse(400)

    def delete(self):
        http_response = ResponseTaskProcessor()
        http_response.success = True
        return http_response.toResponse(200)

