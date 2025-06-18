import os
from app import create_app

app = create_app('development')
celery = app.celery

if __name__ == '__main__':
    celery.start()