from flask import Flask

from task_processor.views import task_processor_bp

app = Flask(__name__)
app.config.from_pyfile('settings.py')

app.register_blueprint(task_processor_bp)

