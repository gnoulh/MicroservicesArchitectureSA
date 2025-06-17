import json
import logging
import pika
from typing import Dict, Any
from celery import Celery

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Celery configuration for async processing
celery_app = Celery('notification_service')
celery_app.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
)

class NotificationConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange_name = 'todo.events'
        self.queue_name = 'notification.queue'
        
    def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            credentials = pika.PlainCredentials('todouser', 'todopass123')
            parameters = pika.ConnectionParameters(
                host='localhost',
                port=5672,
                virtual_host='todo_vhost',
                credentials=credentials
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare exchange and queue
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type='topic',
                durable=True
            )
            
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            
            # Bind queue to exchange with routing keys
            routing_keys = ['task.*', 'project.*', 'user.*']
            for routing_key in routing_keys:
                self.channel.queue_bind(
                    exchange=self.exchange_name,
                    queue=self.queue_name,
                    routing_key=routing_key
                )
            
            logger.info("Connected to RabbitMQ successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    def callback(self, ch, method, properties, body):
        """Process incoming messages"""
        try:
            # Parse message
            message = json.loads(body.decode('utf-8'))
            event_type = message.get('eventType')
            
            logger.info(f"Received event: {event_type}")
            
            # Process different event types
            if event_type == 'task.created':
                self.handle_task_created(message)
            elif event_type == 'task.updated':
                self.handle_task_updated(message)
            elif event_type == 'task.completed':
                self.handle_task_completed(message)
            elif event_type == 'project.created':
                self.handle_project_created(message)
            elif event_type == 'user.registered':
                self.handle_user_registered(message)
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Reject message and requeue
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def handle_task_created(self, message: Dict[str, Any]):
        """Handle task created events"""
        data = message.get('data', {})
        task_id = data.get('taskId')
        assigned_user_id = data.get('assignedUserId')
        
        if assigned_user_id:
            # Send async notification
            send_notification_async.delay(
                user_id=assigned_user_id,
                message=f"New task assigned: {data.get('title')}",
                notification_type='task_assigned'
            )
    
    def handle_task_completed(self, message: Dict[str, Any]):
        """Handle task completed events"""
        data = message.get('data', {})
        completed_by = data.get('completedBy')
        
        send_notification_async.delay(
            user_id=completed_by,
            message="Congratulations! Task completed successfully!",
            notification_type='task_completed'
        )
    
    def handle_project_created(self, message: Dict[str, Any]):
        """Handle project created events"""
        data = message.get('data', {})
        owner_id = data.get('ownerId')
        
        send_notification_async.delay(
            user_id=owner_id,
            message=f"Project '{data.get('name')}' created successfully!",
            notification_type='project_created'
        )
    
    def handle_user_registered(self, message: Dict[str, Any]):
        """Handle user registered events"""
        data = message.get('data', {})
        user_id = data.get('userId')
        
        send_notification_async.delay(
            user_id=user_id,
            message="Welcome to Todo App! Start by creating your first project.",
            notification_type='welcome'
        )
    
    def handle_task_updated(self, message: Dict[str, Any]):
        """Handle task updated events"""
        # Implement based on specific update requirements
        pass
    
    def start_consuming(self):
        """Start consuming messages"""
        if not self.connection or self.connection.is_closed:
            self.connect()
        
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.callback
        )
        
        logger.info("Starting to consume messages...")
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            self.connection.close()

# Celery task for async notification processing
@celery_app.task
def send_notification_async(user_id: str, message: str, notification_type: str):
    """Send notification asynchronously"""
    try:
        # Here you would implement the actual notification sending logic
        # This could include email, SMS, push notifications, etc.
        logger.info(f"Sending {notification_type} notification to user {user_id}: {message}")
        
        # Example: Store notification in database
        # notification_service.create_notification(user_id, message, notification_type)
        
        return True
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        return False

if __name__ == '__main__':
    consumer = NotificationConsumer()
    consumer.start_consuming()