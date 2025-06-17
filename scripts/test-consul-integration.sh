#!/bin/bash

echo "=== Consul Service Registry Integration Test ==="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test functions
check_service() {
    local service_name=$1
    local expected_count=${2:-1}
    
    echo -e "${YELLOW}Testing $service_name...${NC}"
    
    # Check service registration
    response=$(curl -s http://localhost:8500/v1/catalog/service/$service_name)
    count=$(echo $response | jq '. | length')
    
    if [ "$count" -eq "$expected_count" ]; then
        echo -e "${GREEN}✓ $service_name registered successfully ($count instances)${NC}"
    else
        echo -e "${RED}✗ $service_name registration failed (expected $expected_count, got $count)${NC}"
        return 1
    fi
    
    # Check health status
    health_response=$(curl -s http://localhost:8500/v1/health/service/$service_name)
    healthy_count=$(echo $health_response | jq '[.[] | select(.Checks[] | select(.Status == "passing"))] | length')
    
    if [ "$healthy_count" -eq "$expected_count" ]; then
        echo -e "${GREEN}✓ $service_name health checks passing${NC}"
    else
        echo -e "${RED}✗ $service_name health checks failing${NC}"
        return 1
    fi
    
    echo ""
}

check_health_endpoint() {
    local service_name=$1
    local port=$2
    
    echo -e "${YELLOW}Testing $service_name health endpoints...${NC}"
    
    # Test /health
    if curl -s -f "http://localhost:$port/health" > /dev/null; then
        echo -e "${GREEN}✓ $service_name /health endpoint working${NC}"
    else
        echo -e "${RED}✗ $service_name /health endpoint failed${NC}"
        return 1
    fi
    
    # Test /health/live
    if curl -s -f "http://localhost:$port/health/live" > /dev/null; then
        echo -e "${GREEN}✓ $service_name /health/live endpoint working${NC}"
    else
        echo -e "${RED}✗ $service_name /health/live endpoint failed${NC}"
        return 1
    fi
    
    # Test /health/ready
    if curl -s -f "http://localhost:$port/health/ready" > /dev/null; then
        echo -e "${GREEN}✓ $service_name /health/ready endpoint working${NC}"
    else
        echo -e "${RED}✗ $service_name /health/ready endpoint failed${NC}"
        return 1
    fi
    
    echo ""
}

# Wait for services to start
echo "Waiting for services to start..."
sleep 30

# Test Consul availability
echo -e "${YELLOW}Testing Consul availability...${NC}"
if curl -s -f http://localhost:8500/v1/status/leader > /dev/null; then
    echo -e "${GREEN}✓ Consul is running${NC}"
else
    echo -e "${RED}✗ Consul is not accessible${NC}"
    exit 1
fi
echo ""

# Test service registrations
check_service "user-service"
check_service "task-service"
check_service "project-service"
check_service "notification-service"
check_service "analytics-service"
check_service "collaboration-service"

# Test health endpoints
check_health_endpoint "user-service" 8084
check_health_endpoint "task-service" 8085
check_health_endpoint "project-service" 8086
check_health_endpoint "notification-service" 8087
check_health_endpoint "analytics-service" 8088
check_health_endpoint "collaboration-service" 8089

# Test service discovery
echo -e "${YELLOW}Testing service discovery...${NC}"
services=$(curl -s http://localhost:8500/v1/catalog/services | jq -r 'keys[]')
expected_services=("user-service" "task-service" "project-service" "notification-service" "analytics-service" "collaboration-service")

for service in "${expected_services[@]}"; do
    if echo "$services" | grep -q "$service"; then
        echo -e "${GREEN}✓ $service discoverable${NC}"
    else
        echo -e "${RED}✗ $service not discoverable${NC}"
    fi
done

echo ""
echo -e "${GREEN}=== Consul Integration Test Complete ===${NC}"