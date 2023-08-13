from celery import Celery, Task
from flaskblog.config import CELERY_CONFIG
from flask import Flask

class FlaskTask(Task):
    def __call__(self) -> object:
        with app.app_context():
            return self.run()

def celery_init_app(app: Flask) -> Celery:
    celery_app = Celery(app.name, task_cls=FlaskTask,
        broker=CELERY_CONFIG['broker_url'],
        backend=CELERY_CONFIG['result_backend'])
    celery_app.config_from_object(CELERY_CONFIG)
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    celery_app.conf.worker_disable_tracebacks  = True
    return celery_app


#celery -A run.celery worker --pool=solo --loglevel=info
