const axios = require('axios');
const assert = require('assert');

class ConsulIntegrationTest {
    constructor() {
        this.consulUrl = 'http://localhost:8500';
        this.services = [
            { name: 'user-service', port: 8084 },
            { name: 'task-service', port: 8085 },
            { name: 'project-service', port: 8086 },
            { name: 'notification-service', port: 8087 },
            { name: 'analytics-service', port: 8088 },
            { name: 'collaboration-service', port: 8089 }
        ];
    }

    async testConsulHealth() {
        console.log('Testing Consul health...');
        try {
            const response = await axios.get(`${this.consulUrl}/v1/status/leader`);
            assert(response.status === 200, 'Consul should be healthy');
            console.log('✓ Consul is healthy');
        } catch (error) {
            throw new Error(`Consul health check failed: ${error.message}`);
        }
    }

    async testServiceRegistration() {
        console.log('Testing service registration...');
        
        for (const service of this.services) {
            try {
                const response = await axios.get(`${this.consulUrl}/v1/catalog/service/${service.name}`);
                assert(response.data.length > 0, `${service.name} should be registered`);
                console.log(`✓ ${service.name} is registered`);
            } catch (error) {
                throw new Error(`Service registration test failed for ${service.name}: ${error.message}`);
            }
        }
    }

    async testServiceHealth() {
        console.log('Testing service health...');
        
        for (const service of this.services) {
            try {
                const response = await axios.get(`${this.consulUrl}/v1/health/service/${service.name}`);
                const healthyServices = response.data.filter(s => 
                    s.Checks.every(check => check.Status === 'passing')
                );
                assert(healthyServices.length > 0, `${service.name} should have healthy instances`);
                console.log(`✓ ${service.name} has healthy instances`);
            } catch (error) {
                throw new Error(`Service health test failed for ${service.name}: ${error.message}`);
            }
        }
    }

    async testHealthEndpoints() {
        console.log('Testing health endpoints...');
        
        for (const service of this.services) {
            const endpoints = ['/health', '/health/live', '/health/ready'];
            
            for (const endpoint of endpoints) {
                try {
                    const response = await axios.get(`http://localhost:${service.port}${endpoint}`);
                    assert(response.status === 200, `${service.name}${endpoint} should return 200`);
                    assert(response.data.status === 'UP', `${service.name}${endpoint} should return status UP`);
                    console.log(`✓ ${service.name}${endpoint} is working`);
                } catch (error) {
                    throw new Error(`Health endpoint test failed for ${service.name}${endpoint}: ${error.message}`);
                }
            }
        }
    }

    async testServiceDiscovery() {
        console.log('Testing service discovery...');
        
        try {
            const response = await axios.get(`${this.consulUrl}/v1/catalog/services`);
            const registeredServices = Object.keys(response.data);
            
            for (const service of this.services) {
                assert(registeredServices.includes(service.name), 
                    `${service.name} should be discoverable`);
                console.log(`✓ ${service.name} is discoverable`);
            }
        } catch (error) {
            throw new Error(`Service discovery test failed: ${error.message}`);
        }
    }

    async runAllTests() {
        console.log('=== Running Consul Integration Tests ===\n');
        
        try {
            await this.testConsulHealth();
            await this.testServiceRegistration();
            await this.testServiceHealth();
            await this.testHealthEndpoints();
            await this.testServiceDiscovery();
            
            console.log('\n=== All tests passed! ===');
            return true;
        } catch (error) {
            console.error(`\n=== Test failed: ${error.message} ===`);
            return false;
        }
    }
}

// Run tests if called directly
if (require.main === module) {
    const test = new ConsulIntegrationTest();
    test.runAllTests().then(success => {
        process.exit(success ? 0 : 1);
    });
}

module.exports = ConsulIntegrationTest;