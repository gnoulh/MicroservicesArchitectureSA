#!/bin/bash

set -e

echo "=== Deploying Microservices Todo List with Consul Service Registry ==="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
CONSUL_VERSION="1.15.3"
NETWORK_NAME="microservices-network"

# Create network if it doesn't exist
echo -e "${YELLOW}Creating Docker network...${NC}"
docker network create $NETWORK_NAME 2>/dev/null || true

# Function to wait for service
wait_for_service() {
    local service_name=$1
    local port=$2
    local max_attempts=30
    local attempt=0
    
    echo -e "${YELLOW}Waiting for $service_name to be ready...${NC}"
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -f -s "http://localhost:$port/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ $service_name is ready${NC}"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo "Attempt $attempt/$max_attempts - waiting for $service_name..."
        sleep 10
    done
    
    echo -e "${RED}✗ $service_name failed to start${NC}"
    return 1
}

# Step 1: Start infrastructure services
echo -e "${YELLOW}Step 1: Starting infrastructure services...${NC}"
docker-compose up -d consul redis influxdb neo4j
docker-compose up -d user-db task-db project-db

# Wait for Consul
echo -e "${YELLOW}Waiting for Consul to be ready...${NC}"
sleep 15
if curl -f -s "http://localhost:8500/v1/status/leader" > /dev/null; then
    echo -e "${GREEN}✓ Consul is ready${NC}"
else
    echo -e "${RED}✗ Consul failed to start${NC}"
    exit 1
fi

# Step 2: Start application services
echo -e "${YELLOW}Step 2: Starting application services...${NC}"
docker-compose up -d user-service
wait_for_service "user-service" 8084

docker-compose up -d task-service
wait_for_service "task-service" 8085

docker-compose up -d project-service
wait_for_service "project-service" 8086

docker-compose up -d notification-service
wait_for_service "notification-service" 8087

docker-compose up -d analytics-service
wait_for_service "analytics-service" 8088

docker-compose up -d collaboration-service
wait_for_service "collaboration-service" 8089

# Step 3: Start monitoring (optional)
echo -e "${YELLOW}Step 3: Starting monitoring services...${NC}"
docker-compose -f monitoring/consul-monitoring.yml up -d

# Step 4: Verify all services are registered with Consul
echo -e "${YELLOW}Step 4: Verifying service registration...${NC}"
sleep 10

services=("user-service" "task-service" "project-service" "notification-service" "analytics-service" "collaboration-service")
for service in "${services[@]}"; do
    if curl -s "http://localhost:8500/v1/catalog/service/$service" | jq -e '. | length > 0' > /dev/null; then
        echo -e "${GREEN}✓ $service registered with Consul${NC}"
    else
        echo -e "${RED}✗ $service not registered with Consul${NC}"
    fi
done

# Step 5: Run integration tests
echo -e "${YELLOW}Step 5: Running integration tests...${NC}"
chmod +x scripts/test-consul-integration.sh
./scripts/test-consul-integration.sh

echo ""
echo -e "${GREEN}=== Deployment Complete! ===${NC}"
echo ""
echo "Services are available at:"
echo "  - Consul UI: http://localhost:8500"
echo "  - User Service: http://localhost:8084"
echo "  - Task Service: http://localhost:8085"
echo "  - Project Service: http://localhost:8086"
echo "  - Notification Service: http://localhost:8087"
echo "  - Analytics Service: http://localhost:8088"
echo "  - Collaboration Service: http://localhost:8089"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana: http://localhost:3000 (admin/admin)"
echo ""
echo "To view registered services:"
echo "  curl http://localhost:8500/v1/catalog/services | jq"
echo ""
echo "To check service health:"
echo "  curl http://localhost:8500/v1/health/service/<service-name> | jq"