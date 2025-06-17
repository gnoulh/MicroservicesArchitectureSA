package consul

import (
    "fmt"
    "log"
    "os"
    "strconv"
    
    consulapi "github.com/hashicorp/consul/api"
)

type ConsulClient struct {
    client *consulapi.Client
}

func NewConsulClient() (*ConsulClient, error) {
    config := consulapi.DefaultConfig()
    if addr := os.Getenv("CONSUL_HTTP_ADDR"); addr != "" {
        config.Address = addr
    }
    
    client, err := consulapi.NewClient(config)
    if err != nil {
        return nil, err
    }
    
    return &ConsulClient{client: client}, nil
}

func (c *ConsulClient) RegisterService() error {
    serviceName := os.Getenv("SERVICE_NAME")
    serviceID := os.Getenv("SERVICE_ID")
    servicePortStr := os.Getenv("SERVICE_PORT")
    
    servicePort, err := strconv.Atoi(servicePortStr)
    if err != nil {
        return fmt.Errorf("invalid SERVICE_PORT: %v", err)
    }
    
    registration := &consulapi.AgentServiceRegistration{
        ID:   serviceID,
        Name: serviceName,
        Port: servicePort,
        Address: GetLocalIP(),
        Tags: []string{"todo-app", "user-management"},
        Check: &consulapi.AgentServiceCheck{
            HTTP:                           fmt.Sprintf("http://%s:%d/health", GetLocalIP(), servicePort),
            Timeout:                        "10s",
            Interval:                       "30s",
            DeregisterCriticalServiceAfter: "90s",
        },
    }
    
    return c.client.Agent().ServiceRegister(registration)
}

func (c *ConsulClient) DeregisterService() error {
    serviceID := os.Getenv("SERVICE_ID")
    return c.client.Agent().ServiceDeregister(serviceID)
}

func GetLocalIP() string {
    // In Docker environment, return container name or service name
    return os.Getenv("SERVICE_NAME")
}