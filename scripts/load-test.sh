#!/bin/bash

echo "Starting load test for Todo API Gateway..."

# Test user service through gateway
echo "Testing User Service..."
for i in {1..10}; do
    curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/users &
done
wait

# Test task service through gateway
echo "Testing Task Service..."
for i in {1..10}; do
    curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/tasks &
done
wait

# Test project service through gateway
echo "Testing Project Service..."
for i in {1..10}; do
    curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/projects &
done
wait

echo "Load test completed!"