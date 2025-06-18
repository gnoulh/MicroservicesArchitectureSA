package com.todoapp.shared.discovery;

import com.ecwid.consul.v1.ConsulClient;
import com.ecwid.consul.v1.health.model.HealthService;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Random;

@Component
public class ServiceDiscovery {
    
    private final ConsulClient consulClient;
    private final Random random;
    
    public ServiceDiscovery(String consulHost, int consulPort) {
        this.consulClient = new ConsulClient(consulHost, consulPort);
        this.random = new Random();
    }
    
    public List<HealthService> discoverService(String serviceName) {
        return consulClient.getHealthServices(serviceName, true, null).getValue();
    }
    
    public String getServiceUrl(String serviceName) throws Exception {
        List<HealthService> services = discoverService(serviceName);
        
        if (services.isEmpty()) {
            throw new Exception("No healthy instances found for service: " + serviceName);
        }
        
        // Simple load balancing - random selection
        HealthService service = services.get(random.nextInt(services.size()));
        return String.format("http://%s:%d", 
            service.getService().getAddress(), 
            service.getService().getPort());
    }
}