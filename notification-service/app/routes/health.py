from flask import Blueprint, jsonify, current_app
import redis

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check Redis connection
        current_app.redis.ping()
        
        return jsonify({
            'status': 'healthy',
            'service': 'notification-service',
            'version': '1.0.0',
            'redis': 'connected'
        }), 200
        
    except redis.ConnectionError:
        return jsonify({
            'status': 'unhealthy',
            'service': 'notification-service',
            'version': '1.0.0',
            'redis': 'disconnected'
        }), 503
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'notification-service',
            'error': str(e)
        }), 503