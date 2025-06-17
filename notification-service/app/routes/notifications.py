from flask import Blueprint, request, jsonify, current_app

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/send', methods=['POST'])
def send_notification():
    """Send a notification"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['userId', 'type', 'message']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create notification
        notification_service = current_app.notification_service
        notification = notification_service.create_notification(
            user_id=data['userId'],
            notification_type=data['type'],
            title=data.get('title', 'Todo App Notification'),
            message=data['message'],
            channels=data.get('channels', ['in_app']),
            priority=data.get('priority', 'medium'),
            metadata=data.get('metadata', {})
        )
        
        return jsonify({
            'id': notification.id,
            'status': 'queued',
            'message': 'Notification queued for sending'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/user/<user_id>', methods=['GET'])
def get_user_notifications(user_id):
    """Get notifications for a user"""
    try:
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        notification_service = current_app.notification_service
        notifications = notification_service.get_user_notifications(user_id, unread_only)
        
        return jsonify({
            'notifications': [n.to_dict() for n in notifications],
            'count': len(notifications)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/<notification_id>/read', methods=['PUT'])
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    try:
        notification_service = current_app.notification_service
        success = notification_service.mark_as_read(notification_id)
        
        if success:
            return jsonify({'message': 'Notification marked as read'}), 200
        else:
            return jsonify({'error': 'Notification not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/user/<user_id>/preferences', methods=['GET'])
def get_user_preferences(user_id):
    """Get user notification preferences"""
    try:
        notification_service = current_app.notification_service
        preferences = notification_service.get_user_preferences(user_id)
        return jsonify(preferences.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/user/<user_id>/preferences', methods=['PUT'])
def update_user_preferences(user_id):
    """Update user notification preferences"""
    try:
        data = request.get_json()
        notification_service = current_app.notification_service
        preferences = notification_service.update_user_preferences(user_id, data)
        
        return jsonify({
            'message': 'Preferences updated successfully',
            'preferences': preferences.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500