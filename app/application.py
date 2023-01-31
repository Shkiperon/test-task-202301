from flask import Flask, render_template
from werkzeug.routing import BaseConverter
from uuid import UUID
from queue import Queue

from settings import max_lines
from task_processor.views import task_processor_bp
from app_threads.background_workers import FillQueueWorker, CallWorker
from ami_connector.engine import AsteriskListener


class TaskUUID(BaseConverter):

    def __init__(self, url_map):
        super().__init__(url_map)

    def to_python(self, value):
        return UUID(value)


app = Flask(__name__)
app.config.from_pyfile('settings.py')
app.url_map.converters['taskUUID'] = TaskUUID

app.register_blueprint(task_processor_bp)

ami_listener = AsteriskListener()

# prev AsteriskListener doesnt work
# ami_listener.client.add_event_listener(AsteriskListener())

#Maybe redefine maxsize as 'int(max_lines*1.3)'?
CALLTASKS_QUEUE = Queue(maxsize=max_lines)

filler_worker = FillQueueWorker(CALLTASKS_QUEUE)
filler_worker.daemon = True
filler_worker.start()

for i in range(max_lines):
    call_worker = CallWorker(CALLTASKS_QUEUE)
    call_worker.daemon = True
    call_worker.start()

@app.route('/autocall')
def upload_file_form():
    return render_template('html/upload.html')

