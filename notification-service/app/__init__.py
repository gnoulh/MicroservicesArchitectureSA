from flask import Flask
from flask_cors import CORS
from celery import Celery
import redis
from config.config import config
from app.services.notification_service import NotificationService

def create_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    CORS(app)
    
    # Initialize Redis
    app.redis = redis.from_url(app.config['REDIS_URL'])
    
    # Initialize Celery
    app.celery = create_celery(app)

    # Instantiate and attach EmailService
    app.notification_service = NotificationService(app.config)
    
    # Register blueprints
    from app.routes.notifications import notifications_bp
    from app.routes.health import health_bp
    
    app.register_blueprint(notifications_bp, url_prefix='/notifications')
    app.register_blueprint(health_bp)
    
    return app

def signal_handler(sig, frame):
    print('Gracefully shutting down...')
    from app.consul_client import consul_client
    consul_client.deregister_service()
    sys.exit(0)
