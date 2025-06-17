from flask import Blueprint, jsonify
import redis
import datetime
import os

health_bp = Blueprint('health', __name__)

def get_redis_client():
    return redis.Redis(
        host=os.getenv('REDIS_HOST', 'redis'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        decode_responses=True
    )

@health_bp.route('/health')
def health():
    return readiness()

@health_bp.route('/health/live')
def liveness():
    response = {
        'status': 'UP',
        'timestamp': datetime.datetime.now().isoformat(),
        'checks': {}
    }
    return jsonify(response)

@health_bp.route('/health/ready')
def readiness():
    response = {
        'status': 'UP',
        'timestamp': datetime.datetime.now().isoformat(),
        'checks': {}
    }
    
    try:
        # Check Redis connectivity
        r = get_redis_client()
        r.ping()
        response['checks']['redis'] = 'OK'
    except Exception as e:
        response['status'] = 'DOWN'
        response['checks']['redis'] = f'FAIL: {str(e)}'
        return jsonify(response), 503
    
    return jsonify(response)