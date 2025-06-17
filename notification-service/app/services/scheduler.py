from celery import current_app
from celery.schedules import crontab
from datetime import datetime, timedelta
import requests

def setup_periodic_tasks():
    """Setup periodic tasks for notifications"""
    
    # Daily summary at 8 AM
    current_app.conf.beat_schedule = {
        'daily-summary': {
            'task': 'app.tasks.notification_tasks.send_daily_summary_task',
            'schedule': crontab(hour=8, minute=0),  # 8:00 AM daily
        },
        'cleanup-old-notifications': {
            'task': 'app.tasks.notification_tasks.cleanup_old_notifications_task',
            'schedule': crontab(hour=2, minute=0),  # 2:00 AM daily
        },
        'check-due-tasks': {
            'task': 'app.tasks.notification_tasks.check_due_tasks_task',
            'schedule': crontab(minute='*/30'),  # Every 30 minutes
        },
    }
    
    current_app.conf.timezone = 'UTC'

def check_due_tasks():
    """Check for tasks that are due soon and send reminders"""
    try:
        # Get tasks due in the next 24 hours
        response = requests.get(
            f"{current_app.config['TASK_SERVICE_URL']}/tasks/due-soon",
            timeout=10
        )
        
        if response.status_code == 200:
            due_tasks = response.json()
            
            for task in due_tasks:
                # Send reminder notification
                from app.services.notification_service import NotificationService
                notification_service = NotificationService()
                
                # Check if reminder already sent
                if not task.get('reminder_sent', False):
                    notification_service.create_notification(
                        user_id=task['assigned_user_id'],
                        notification_type='task_due_reminder',
                        title='Task Due Reminder',
                        message=f"Task '{task['title']}' is due soon!",
                        channels=['in_app', 'email'],
                        priority='high',
                        metadata={
                            'task_id': task['id'],
                            'task_title': task['title'],
                            'due_date': task['due_date']
                        }
                    )
                    
                    # Mark reminder as sent (would need API endpoint in task service)
                    requests.put(
                        f"{current_app.config['TASK_SERVICE_URL']}/tasks/{task['id']}/reminder-sent",
                        timeout=5
                    )
                    
    except Exception as e:
        print(f"Error checking due tasks: {e}")