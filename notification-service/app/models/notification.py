from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
import json

@dataclass
class Notification:
    id: str
    user_id: str
    type: str
    title: str
    message: str
    channels: list  # ['email', 'sms', 'in_app']
    priority: str  # 'low', 'medium', 'high'
    status: str  # 'pending', 'sent', 'failed', 'read'
    created_at: datetime
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'channels': self.channels,
            'priority': self.priority,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            user_id=data['user_id'],
            type=data['type'],
            title=data['title'],
            message=data['message'],
            channels=data['channels'],
            priority=data['priority'],
            status=data['status'],
            created_at=datetime.fromisoformat(data['created_at']),
            sent_at=datetime.fromisoformat(data['sent_at']) if data.get('sent_at') else None,
            read_at=datetime.fromisoformat(data['read_at']) if data.get('read_at') else None,
            metadata=data.get('metadata')
        )

@dataclass
class NotificationPreferences:
    user_id: str
    email_enabled: bool = True
    sms_enabled: bool = False
    in_app_enabled: bool = True
    task_due_reminder: bool = True
    task_assigned: bool = True
    project_updates: bool = True
    daily_summary: bool = False
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'email_enabled': self.email_enabled,
            'sms_enabled': self.sms_enabled,
            'in_app_enabled': self.in_app_enabled,
            'task_due_reminder': self.task_due_reminder,
            'task_assigned': self.task_assigned,
            'project_updates': self.project_updates,
            'daily_summary': self.daily_summary
        }