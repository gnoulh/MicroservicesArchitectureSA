const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
require('dotenv').config();

const projectRoutes = require('./routes/projects');
const rabbitMQPublisher = require('./config/rabbitmq');
const mysql = require('mysql2/promise');
const HealthController = require('./health/healthController');
const ConsulClient = require('./consul/consulClient');

// Initialize connection on startup
rabbitMQPublisher.connect();

const app = express();
const PORT = process.env.PORT || 8086;

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health controller
const healthController = new HealthController(dbConfig);

// Health endpoints
app.get('/health', (req, res) => healthController.health(req, res));
app.get('/health/live', (req, res) => healthController.liveness(req, res));
app.get('/health/ready', (req, res) => healthController.readiness(req, res));

// Routes
app.use('/projects', projectRoutes);
app.post('/projects', async (req, res) => {
    const project = await projectService.create(req.body);
    await rabbitMQPublisher.publishProjectCreated(project);
    res.json(project);
});

// Consul registration
const consulClient = new ConsulClient();

// Graceful shutdown
process.on('SIGTERM', async () => {
    console.log('SIGTERM received, shutting down gracefully');
    await consulClient.deregisterService();
    process.exit(0);
});

process.on('SIGINT', async () => {
    console.log('SIGINT received, shutting down gracefully');
    await consulClient.deregisterService();
    process.exit(0);
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

app.listen(PORT, async () => {
  console.log(`Project service running on port ${PORT}`);
  await consulClient.registerService();
});

module.exports = app;