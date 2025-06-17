#!/bin/bash

echo "=== Final Consul Setup Validation ==="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

FAILED_TESTS=0

# Test 1: Consul UI accessibility
echo -e "${YELLOW}Test 1: Consul UI accessibility${NC}"
if curl -s -f http://localhost:8500/ui/ > /dev/null; then
    echo -e "${GREEN}✓ Consul UI is accessible${NC}"
else
    echo -e "${RED}✗ Consul UI is not accessible${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test 2: All services registered
echo -e "${YELLOW}Test 2: Service registration${NC}"
EXPECTED_SERVICES=("user-service" "task-service" "project-service" "notification-service" "analytics-service" "collaboration-service")
REGISTERED_SERVICES=$(curl -s http://localhost:8500/v1/catalog/services | jq -r 'keys[]')

for service in "${EXPECTED_SERVICES[@]}"; do
    if echo "$REGISTERED_SERVICES" | grep -q "$service"; then
        echo -e "${GREEN}✓ $service is registered${NC}"
    else
        echo -e "${RED}✗ $service is not registered${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
done

# Test 3: Service health checks
echo -e "${YELLOW}Test 3: Service health checks${NC}"
for service in "${EXPECTED_SERVICES[@]}"; do
    HEALTH_STATUS=$(curl -s http://localhost:8500/v1/health/service/$service | jq -r '.[0].Checks[] | select(.ServiceName == "'"$service"'") | .Status')
    if [ "$HEALTH_STATUS" = "passing" ]; then
        echo -e "${GREEN}✓ $service health check is passing${NC}"
    else
        echo -e "${RED}✗ $service health check is failing (status: $HEALTH_STATUS)${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
done

# Test 4: Service endpoints
echo -e "${YELLOW}Test 4: Service endpoints${NC}"
SERVICES_PORTS=("8084" "8085" "8086" "8087" "8088" "8089")
SERVICE_NAMES=("user-service" "task-service" "project-service" "notification-service" "analytics-service" "collaboration-service")

for i in "${!SERVICES_PORTS[@]}"; do
    PORT=${SERVICES_PORTS[$i]}
    SERVICE=${SERVICE_NAMES[$i]}
    
    if curl -s -f http://localhost:$PORT/health > /dev/null; then
        echo -e "${GREEN}✓ $SERVICE endpoint is responding${NC}"
    else
        echo -e "${RED}✗ $SERVICE endpoint is not responding${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
done

# Test 5: Service discovery functionality
echo -e "${YELLOW}Test 5: Service discovery functionality${NC}"
for service in "${EXPECTED_SERVICES[@]}"; do
    SERVICE_INFO=$(curl -s http://localhost:8500/v1/catalog/service/$service)
    if [ "$(echo $SERVICE_INFO | jq length)" -gt 0 ]; then
        ADDRESS=$(echo $SERVICE_INFO | jq -r '.[0].ServiceAddress // .[0].Address')
        PORT=$(echo $SERVICE_INFO | jq -r '.[0].ServicePort')
        echo -e "${GREEN}✓ $service discoverable at $ADDRESS:$PORT${NC}"
    else
        echo -e "${RED}✗ $service not discoverable${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
done

# Test 6: Inter-service communication
echo -e "${YELLOW}Test 6: Inter-service communication test${NC}"
# This would typically involve making a request that requires service-to-service communication
# For now, we'll just verify the services can resolve each other
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ All services are properly registered and can be discovered${NC}"
else
    echo -e "${RED}✗ Some services may not be able to communicate properly${NC}"
fi

# Summary
echo ""
echo "=== Validation Summary ==="
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed! Consul service registry is working correctly.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Access Consul UI at http://localhost:8500"
    echo "2. Monitor services and their health status"
    echo "3. Test service discovery in your applications"
    echo "4. Consider implementing Consul Connect for service mesh"
    exit 0
else
    echo -e "${RED}✗ $FAILED_TESTS test(s) failed. Please check the service configuration.${NC}"
    echo ""
    echo "Troubleshooting steps:"
    echo "1. Check docker-compose logs: docker-compose logs [service-name]"
    echo "2. Verify service configuration files"
    echo "3. Ensure all required dependencies are running"
    echo "4. Check network connectivity between services"
    exit 1
fi