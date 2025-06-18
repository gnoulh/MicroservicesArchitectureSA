package discovery

import (
    "fmt"
    "math/rand"
    "time"
    
    consulapi "github.com/hashicorp/consul/api"
)

type ServiceDiscovery struct {
    client *consulapi.Client
}

type ServiceInstance struct {
    ID      string
    Address string
    Port    int
    Tags    []string
}

func NewServiceDiscovery(consulAddr string) (*ServiceDiscovery, error) {
    config := consulapi.DefaultConfig()
    if consulAddr != "" {
        config.Address = consulAddr
    }
    
    client, err := consulapi.NewClient(config)
    if err != nil {
        return nil, err
    }
    
    return &ServiceDiscovery{client: client}, nil
}

func (sd *ServiceDiscovery) DiscoverService(serviceName string) ([]ServiceInstance, error) {
    services, _, err := sd.client.Health().Service(serviceName, "", true, nil)
    if err != nil {
        return nil, err
    }
    
    var instances []ServiceInstance
    for _, service := range services {
        instances = append(instances, ServiceInstance{
            ID:      service.Service.ID,
            Address: service.Service.Address,
            Port:    service.Service.Port,
            Tags:    service.Service.Tags,
        })
    }
    
    return instances, nil
}

func (sd *ServiceDiscovery) GetServiceURL(serviceName string) (string, error) {
    instances, err := sd.DiscoverService(serviceName)
    if err != nil {
        return "", err
    }
    
    if len(instances) == 0 {
        return "", fmt.Errorf("no healthy instances found for service: %s", serviceName)
    }
    
    // Simple load balancing - random selection
    rand.Seed(time.Now().UnixNano())
    instance := instances[rand.Intn(len(instances))]
    
    return fmt.Sprintf("http://%s:%d", instance.Address, instance.Port), nil
}