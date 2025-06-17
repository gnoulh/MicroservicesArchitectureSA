import uuid
import json
from datetime import datetime
from typing import List, Optional
from flask import current_app
from app.models.notification import Notification, NotificationPreferences
from app.services.email_service import EmailService
from app.services.sms_service import SMSService

class NotificationService:
    def __init__(self, config):
        self.email_service = EmailService(config)
        self.sms_service = SMSService(config)
    
    def create_notification(self, user_id: str, notification_type: str, 
                          title: str, message: str, channels: List[str], 
                          priority: str = 'medium', metadata: dict = None) -> Notification:
        """Create a new notification"""
        notification = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            channels=channels,
            priority=priority,
            status='pending',
            created_at=datetime.now(),
            metadata=metadata or {}
        )
        
        # Store in Redis
        self._store_notification(notification)
        
        # Queue for sending
        self._queue_notification(notification)
        
        return notification
    
    def send_notification(self, notification_id: str) -> bool:
        """Send a notification via all specified channels"""
        notification = self.get_notification(notification_id)
        if not notification:
            return False
        
        # Get user preferences
        preferences = self.get_user_preferences(notification.user_id)
        
        success = True
        
        # Send via each channel
        for channel in notification.channels:
            if channel == 'email' and preferences.email_enabled:
                success &= self.email_service.send_email(
                    notification.user_id,
                    notification.title,
                    notification.message,
                    notification.metadata
                )
            elif channel == 'sms' and preferences.sms_enabled:
                success &= self.sms_service.send_sms(
                    notification.user_id,
                    notification.message
                )
            elif channel == 'in_app' and preferences.in_app_enabled:
                # In-app notifications are stored in Redis
                self._store_in_app_notification(notification)
        
        # Update notification status
        notification.status = 'sent' if success else 'failed'
        notification.sent_at = datetime.now()
        self._store_notification(notification)
        
        return success
    
    def get_notification(self, notification_id: str) -> Optional[Notification]:
        """Get a notification by ID"""
        data = current_app.redis.get(f"notification:{notification_id}")
        if data:
            return Notification.from_dict(json.loads(data))
        return None
    
    def get_user_notifications(self, user_id: str, unread_only: bool = False) -> List[Notification]:
        """Get all notifications for a user"""
        pattern = f"user_notifications:{user_id}:*"
        keys = current_app.redis.keys(pattern)
        notifications = []
        
        for key in keys:
            data = current_app.redis.get(key)
            if data:
                notification = Notification.from_dict(json.loads(data))
                if not unread_only or notification.status != 'read':
                    notifications.append(notification)
        
        return sorted(notifications, key=lambda x: x.created_at, reverse=True)
    
    def mark_as_read(self, notification_id: str) -> bool:
        """Mark a notification as read"""
        notification = self.get_notification(notification_id)
        if notification:
            notification.status = 'read'
            notification.read_at = datetime.now()
            self._store_notification(notification)
            return True
        return False
    
    def get_user_preferences(self, user_id: str) -> NotificationPreferences:
        """Get user notification preferences"""
        data = current_app.redis.get(f"user_preferences:{user_id}")
        if data:
            prefs_dict = json.loads(data)
            return NotificationPreferences(**prefs_dict)
        
        # Return default preferences
        return NotificationPreferences(user_id=user_id)
    
    def update_user_preferences(self, user_id: str, preferences: dict) -> NotificationPreferences:
        """Update user notification preferences"""
        current_prefs = self.get_user_preferences(user_id)
        
        # Update preferences
        for key, value in preferences.items():
            if hasattr(current_prefs, key):
                setattr(current_prefs, key, value)
        
        # Store updated preferences
        current_app.redis.set(
            f"user_preferences:{user_id}",
            json.dumps(current_prefs.to_dict()),
            ex=86400 * 30  # 30 days
        )
        
        return current_prefs
    
    def _store_notification(self, notification: Notification):
        """Store notification in Redis"""
        # Store by ID
        current_app.redis.set(
            f"notification:{notification.id}",
            json.dumps(notification.to_dict()),
            ex=86400 * 30  # 30 days
        )
        
        # Store by user ID for easy retrieval
        current_app.redis.set(
            f"user_notifications:{notification.user_id}:{notification.id}",
            json.dumps(notification.to_dict()),
            ex=86400 * 30  # 30 days
        )
    
    def _store_in_app_notification(self, notification: Notification):
        """Store in-app notification"""
        current_app.redis.zadd(
            f"in_app_notifications:{notification.user_id}",
            {notification.id: notification.created_at.timestamp()}
        )
    
    def _queue_notification(self, notification: Notification):
        """Queue notification for async processing"""
        from app.tasks.notification_tasks import send_notification_task
        send_notification_task.delay(notification.id)