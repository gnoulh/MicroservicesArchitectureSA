import consul
import os
import socket
import atexit

class ConsulClient:
    def __init__(self):
        self.service_name = os.getenv('SERVICE_NAME', 'notification-service')
        self.service_id = os.getenv('SERVICE_ID', 'notification-service-1')
        self.service_port = int(os.getenv('SERVICE_PORT', 8087))
        
        consul_host = os.getenv('CONSUL_HTTP_ADDR', 'consul:8500').split(':')
        self.consul = consul.Consul(host=consul_host[0], port=int(consul_host[1]))
        
    def register_service(self):
        try:
            self.consul.agent.service.register(
                name=self.service_name,
                service_id=self.service_id,
                address=self.service_name,  # Use service name in Docker
                port=self.service_port,
                tags=['todo-app', 'notifications'],
                check=consul.Check.http(
                    f'http://{self.service_name}:{self.service_port}/health',
                    interval='30s',
                    timeout='10s',
                    deregister='90s'
                )
            )
            print(f'Service registered with Consul: {self.service_name}')
        except Exception as e:
            print(f'Failed to register service with Consul: {e}')
    
    def deregister_service(self):
        try:
            self.consul.agent.service.deregister(self.service_id)
            print(f'Service deregistered from Consul: {self.service_name}')
        except Exception as e:
            print(f'Failed to deregister service from Consul: {e}')

# Global instance
consul_client = ConsulClient()

def register_with_consul():
    consul_client.register_service()
    atexit.register(consul_client.deregister_service)