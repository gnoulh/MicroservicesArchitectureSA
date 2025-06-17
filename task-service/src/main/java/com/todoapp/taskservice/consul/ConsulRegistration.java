package com.todoapp.taskservice.consul;

import com.ecwid.consul.v1.ConsulClient;
import com.ecwid.consul.v1.agent.model.NewService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;
import java.net.InetAddress;
import java.util.Arrays;

@Component
public class ConsulRegistration {

    private ConsulClient consulClient;

    @Value("${consul.host:consul}")
    private String consulHost;

    @Value("${consul.port:8500}")
    private int consulPort;

    @Value("${spring.application.name:task-service}")
    private String serviceName;

    @Value("${server.port:8085}")
    private int servicePort;

    @Value("${service.id:task-service-1}")
    private String serviceId;

    @PostConstruct
    public void registerService() {
        try {
            consulClient = new ConsulClient(consulHost, consulPort);
            
            NewService newService = new NewService();
            newService.setId(serviceId);
            newService.setName(serviceName);
            newService.setPort(servicePort);
            newService.setAddress(getServiceAddress());
            newService.setTags(Arrays.asList("todo-app", "task-management"));
            
            NewService.Check check = new NewService.Check();
            check.setHttp(String.format("http://%s:%d/health", getServiceAddress(), servicePort));
            check.setInterval("30s");
            check.setTimeout("10s");
            check.setDeregisterCriticalServiceAfter("90s");
            newService.setCheck(check);
            
            consulClient.agentServiceRegister(newService);
            System.out.println("Service registered with Consul: " + serviceName);
            
        } catch (Exception e) {
            System.err.println("Failed to register service with Consul: " + e.getMessage());
        }
    }

    @PreDestroy
    public void deregisterService() {
        if (consulClient != null) {
            try {
                consulClient.agentServiceDeregister(serviceId);
                System.out.println("Service deregistered from Consul: " + serviceName);
            } catch (Exception e) {
                System.err.println("Failed to deregister service from Consul: " + e.getMessage());
            }
        }
    }

    private String getServiceAddress() {
        return serviceName; // In Docker environment, use service name
    }
}