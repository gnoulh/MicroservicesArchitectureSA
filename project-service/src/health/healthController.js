const mysql = require('mysql2/promise');
const consul = require('consul')();

class HealthController {
    constructor(dbConfig) {
        this.dbConfig = dbConfig;
    }

    async liveness(req, res) {
        const response = {
            status: 'UP',
            timestamp: new Date().toISOString(),
            checks: {}
        };
        
        res.json(response);
    }

    async readiness(req, res) {
        const response = {
            status: 'UP',
            timestamp: new Date().toISOString(),
            checks: {}
        };

        try {
            // Check database connectivity
            const connection = await mysql.createConnection(this.dbConfig);
            await connection.ping();
            await connection.end();
            
            response.checks.database = 'OK';
        } catch (error) {
            response.status = 'DOWN';
            response.checks.database = `FAIL: ${error.message}`;
            return res.status(503).json(response);
        }

        res.json(response);
    }

    async health(req, res) {
        return this.readiness(req, res);
    }
}

module.exports = HealthController;