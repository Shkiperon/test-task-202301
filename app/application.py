from flask import Flask
from werkzeug.routing import BaseConverter
from uuid import UUID

from task_processor.views import task_processor_bp


class TaskUUID(BaseConverter):

    def __init__(self, url_map):
        super().__init__(url_map)

    def to_python(self, value):
        return UUID(value)


app = Flask(__name__)
app.config.from_pyfile('settings.py')
app.url_map.converters['taskUUID'] = TaskUUID

app.register_blueprint(task_processor_bp)

