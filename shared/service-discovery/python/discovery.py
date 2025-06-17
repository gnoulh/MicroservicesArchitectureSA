import consul
import random

class ServiceDiscovery:
    def __init__(self, consul_host='consul', consul_port=8500):
        self.consul = consul.Consul(host=consul_host, port=consul_port)
    
    def discover_service(self, service_name):
        try:
            _, services = self.consul.health.service(service_name, passing=True)
            return [
                {
                    'id': service['Service']['ID'],
                    'address': service['Service']['Address'],
                    'port': service['Service']['Port'],
                    'tags': service['Service']['Tags']
                }
                for service in services
            ]
        except Exception as e:
            raise Exception(f"Failed to discover service {service_name}: {str(e)}")
    
    def get_service_url(self, service_name):
        instances = self.discover_service(service_name)
        
        if not instances:
            raise Exception(f"No healthy instances found for service: {service_name}")
        
        # Simple load balancing - random selection
        instance = random.choice(instances)
        return f"http://{instance['address']}:{instance['port']}"