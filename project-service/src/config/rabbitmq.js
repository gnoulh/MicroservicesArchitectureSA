const amqp = require('amqplib');

class RabbitMQPublisher {
    constructor() {
        this.connection = null;
        this.channel = null;
        this.exchangeName = 'todo.events';
    }

    async connect() {
        try {
            this.connection = await amqp.connect({
                protocol: 'amqp',
                hostname: 'localhost',
                port: 5672,
                username: 'todouser',
                password: 'todopass123',
                vhost: 'todo_vhost'
            });

            this.channel = await this.connection.createChannel();
            await this.channel.assertExchange(this.exchangeName, 'topic', { durable: true });
            
            console.log('Connected to RabbitMQ successfully');
        } catch (error) {
            console.error('Failed to connect to RabbitMQ:', error);
            throw error;
        }
    }

    async publishProjectCreated(project) {
        const event = this.createBaseEvent('project.created');
        event.data = {
            projectId: project.id,
            name: project.name,
            description: project.description,
            ownerId: project.owner_id,
            members: project.members || []
        };

        await this.publish('project.created', event);
    }

    async publishProjectUpdated(project, changes) {
        const event = this.createBaseEvent('project.updated');
        event.data = {
            projectId: project.id,
            changes: changes,
            updatedBy: project.updated_by
        };

        await this.publish('project.updated', event);
    }

    async publish(routingKey, message) {
        if (!this.channel) {
            await this.connect();
        }

        try {
            const messageBuffer = Buffer.from(JSON.stringify(message));
            await this.channel.publish(
                this.exchangeName,
                routingKey,
                messageBuffer,
                { persistent: true }
            );
            console.log(`Published event: ${routingKey}`);
        } catch (error) {
            console.error('Failed to publish message:', error);
            throw error;
        }
    }

    createBaseEvent(eventType) {
        return {
            eventId: require('uuid').v4(),
            timestamp: new Date().toISOString(),
            eventType: eventType,
            version: '1.0'
        };
    }

    async close() {
        if (this.connection) {
            await this.connection.close();
        }
    }
}

module.exports = new RabbitMQPublisher();