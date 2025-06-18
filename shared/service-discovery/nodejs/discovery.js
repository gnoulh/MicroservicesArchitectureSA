const consul = require('consul')();

class ServiceDiscovery {
    constructor(consulOptions = {}) {
        this.consul = consul;
    }

    async discoverService(serviceName) {
        try {
            const result = await this.consul.health.service({
                service: serviceName,
                passing: true
            });
            
            return result.map(service => ({
                id: service.Service.ID,
                address: service.Service.Address,
                port: service.Service.Port,
                tags: service.Service.Tags
            }));
        } catch (error) {
            throw new Error(`Failed to discover service ${serviceName}: ${error.message}`);
        }
    }

    async getServiceUrl(serviceName) {
        const instances = await this.discoverService(serviceName);
        
        if (instances.length === 0) {
            throw new Error(`No healthy instances found for service: ${serviceName}`);
        }
        
        // Simple load balancing - random selection
        const instance = instances[Math.floor(Math.random() * instances.length)];
        return `http://${instance.address}:${instance.port}`;
    }
}

module.exports = ServiceDiscovery;