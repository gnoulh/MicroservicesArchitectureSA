const consul = require('consul')();

class ConsulClient {
    constructor() {
        this.serviceName = process.env.SERVICE_NAME || 'project-service';
        this.serviceId = process.env.SERVICE_ID || 'project-service-1';
        this.servicePort = parseInt(process.env.SERVICE_PORT) || 8086;
        this.consulHost = process.env.CONSUL_HTTP_ADDR || 'consul:8500';
    }

    async registerService() {
        try {
            await consul.agent.service.register({
                id: this.serviceId,
                name: this.serviceName,
                address: this.serviceName, // Use service name in Docker
                port: this.servicePort,
                tags: ['todo-app', 'project-management'],
                check: {
                    http: `http://${this.serviceName}:${this.servicePort}/health`,
                    interval: '30s',
                    timeout: '10s',
                    deregistercriticalserviceafter: '90s'
                }
            });
            
            console.log(`Service registered with Consul: ${this.serviceName}`);
        } catch (error) {
            console.error('Failed to register service with Consul:', error.message);
        }
    }

    async deregisterService() {
        try {
            await consul.agent.service.deregister(this.serviceId);
            console.log(`Service deregistered from Consul: ${this.serviceName}`);
        } catch (error) {
            console.error('Failed to deregister service from Consul:', error.message);
        }
    }
}

module.exports = ConsulClient;