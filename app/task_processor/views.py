from flask import Blueprint

from task_processor.api import TaskProcessor

task_processor_bp = Blueprint('task_processor_bp', __name__)

task_processor_view = TaskProcessor.as_view('task_processor_api')
task_processor_bp.add_url_rule(
    '/autocall/start/',
    view_func=task_processor_view,
    methods=['POST', ]
)
task_processor_bp.add_url_rule(
    '/autocall/stop/<taskUUID:task_id>',
    view_func=task_processor_view,
    methods=['DELETE', ]
)

