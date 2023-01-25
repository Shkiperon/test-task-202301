from flask import Response
from typing import Optional
import json

from settings import ALLOWED_EXTENSIONS

def allowed_file(filename: str):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class ResponseError():
    code: Optional[str]
    message: Optional[str]

    def __init__(self, err_type: Optional[str] = None, err_message: Optional[str] = None):
        self.code = err_type
        self.message = err_message


class ResponseTaskProcessor():
    success: bool
    error: ResponseError

    def __init__(self):
        self.success = False
        self.error = ResponseError()

    def toJson(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            ident=4
        )

    def toResponse(self, http_code: int = 200):
        return Response(self.toJson(), http_code, mimetype='application/json')

