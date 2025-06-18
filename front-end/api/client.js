const ServiceDiscovery = require('../../shared/service-discovery/nodejs/discovery');

class ApiClient {
    constructor() {
        this.serviceDiscovery = new ServiceDiscovery();
        this.serviceCache = new Map();
        this.cacheTimeout = 30000; // 30 seconds
    }

    async getServiceUrl(serviceName) {
        const cacheKey = serviceName;
        const cached = this.serviceCache.get(cacheKey);
        
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.url;
        }
        
        try {
            const url = await this.serviceDiscovery.getServiceUrl(serviceName);
            this.serviceCache.set(cacheKey, { url, timestamp: Date.now() });
            return url;
        } catch (error) {
            // Fallback to cached value if available
            if (cached) {
                return cached.url;
            }
            throw error;
        }
    }

    async getUserService() {
        return await this.getServiceUrl('user-service');
    }

    async getTaskService() {
        return await this.getServiceUrl('task-service');
    }

    async getProjectService() {
        return await this.getServiceUrl('project-service');
    }

    async getNotificationService() {
        return await this.getServiceUrl('notification-service');
    }

    async getAnalyticsService() {
        return await this.getServiceUrl('analytics-service');
    }

    async getCollaborationService() {
        return await this.getServiceUrl('collaboration-service');
    }
}

module.exports = new ApiClient();