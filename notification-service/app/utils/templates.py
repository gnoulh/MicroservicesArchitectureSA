"""
Notification message templates
"""

NOTIFICATION_TEMPLATES = {
    'task_due_reminder': {
        'title': 'Task Due Reminder',
        'email_template': '''
        <h2>Task Due Reminder</h2>
        <p>Hello!</p>
        <p>This is a reminder that your task "<strong>{task_title}</strong>" is due {due_time}.</p>
        <div style="background-color: #f0f8ff; padding: 15px; border-left: 4px solid #007cba; margin: 20px 0;">
            <h3>Task Details:</h3>
            <p><strong>Title:</strong> {task_title}</p>
            <p><strong>Due Date:</strong> {due_date}</p>
            <p><strong>Priority:</strong> {priority}</p>
        </div>
        <p><a href="{task_url}" style="background-color: #007cba; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Task</a></p>
        ''',
        'sms_template': 'Task "{task_title}" is due {due_time}! Check your Todo app for details.'
    },
    
    'task_assigned': {
        'title': 'New Task Assigned',
        'email_template': '''
        <h2>New Task Assigned</h2>
        <p>Hello!</p>
        <p>You have been assigned a new task by {assigned_by}.</p>
        <div style="background-color: #f0f8ff; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0;">
            <h3>Task Details:</h3>
            <p><strong>Title:</strong> {task_title}</p>
            <p><strong>Description:</strong> {task_description}</p>
            <p><strong>Due Date:</strong> {due_date}</p>
            <p><strong>Priority:</strong> {priority}</p>
        </div>
        <p><a href="{task_url}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Task</a></p>
        ''',
        'sms_template': 'New task assigned: "{task_title}" by {assigned_by}. Check your Todo app.'
    },
    
    'project_update': {
        'title': 'Project Update',
        'email_template': '''
        <h2>Project Update</h2>
        <p>Hello!</p>
        <p>There has been an update to project "{project_name}".</p>
        <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
            <p><strong>Update:</strong> {update_message}</p>
            <p><strong>Updated by:</strong> {updated_by}</p>
            <p><strong>Date:</strong> {update_date}</p>
        </div>
        <p><a href="{project_url}" style="background-color: #ffc107; color: black; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Project</a></p>
        ''',
        'sms_template': 'Project "{project_name}" updated: {update_message}'
    },
    
    'daily_summary': {
        'title': 'Daily Task Summary',
        'email_template': '''
        <h2>Your Daily Task Summary</h2>
        <p>Hello!</p>
        <p>Here's your task summary for today:</p>
        
        <div style="background-color: #d4edda; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0;">
            <h3>✅ Completed Tasks ({completed_count})</h3>
            {completed_tasks_html}
        </div>
        
        <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
            <h3>⏰ Pending Tasks ({pending_count})</h3>
            {pending_tasks_html}
        </div>
        
        <div style="background-color: #f8d7da; padding: 15px; border-left: 4px solid #dc3545; margin: 20px 0;">
            <h3>🚨 Overdue Tasks ({overdue_count})</h3>
            {overdue_tasks_html}
        </div>
        
        <p><a href="{dashboard_url}" style="background-color: #007cba; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Dashboard</a></p>
        '''
    }
}

def get_notification_template(notification_type: str, channel: str = 'email'):
    """Get notification template"""
    template = NOTIFICATION_TEMPLATES.get(notification_type, {})
    
    if channel == 'email':
        return template.get('email_template', '')
    elif channel == 'sms':
        return template.get('sms_template', '')
    
    return ''

def format_notification_content(notification_type: str, channel: str, **kwargs):
    """Format notification content with provided data"""
    template = get_notification_template(notification_type, channel)
    
    try:
        return template.format(**kwargs)
    except KeyError as e:
        print(f"Missing template variable: {e}")
        return template