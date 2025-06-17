#!/bin/bash
# RabbitMQ Exchange and Queue Setup Script

RABBITMQ_HOST="localhost"
RABBITMQ_PORT="15672"
RABBITMQ_USER="todouser"
RABBITMQ_PASS="todopass123"
RABBITMQ_VHOST="todo_vhost"

# Wait for RabbitMQ to be ready
echo "Waiting for RabbitMQ to be ready..."
sleep 10

# Create exchanges
curl -u $RABBITMQ_USER:$RABBITMQ_PASS -X PUT \
  http://$RABBITMQ_HOST:$RABBITMQ_PORT/api/exchanges/$RABBITMQ_VHOST/todo.events \
  -H "Content-Type: application/json" \
  -d '{"type":"topic","durable":true}'

# Create queues
declare -a queues=(
  "task.events"
  "project.events" 
  "user.events"
  "notification.queue"
  "analytics.queue"
  "collaboration.queue"
)

for queue in "${queues[@]}"; do
  curl -u $RABBITMQ_USER:$RABBITMQ_PASS -X PUT \
    http://$RABBITMQ_HOST:$RABBITMQ_PORT/api/queues/$RABBITMQ_VHOST/$queue \
    -H "Content-Type: application/json" \
    -d '{"durable":true,"auto_delete":false}'
done

# Create bindings
declare -a bindings=(
  "notification.queue:task.*"
  "notification.queue:project.*"
  "notification.queue:user.*"
  "analytics.queue:task.*"
  "analytics.queue:project.*"
  "analytics.queue:user.*"
  "collaboration.queue:task.*"
  "collaboration.queue:project.*"
)

for binding in "${bindings[@]}"; do
  queue=$(echo $binding | cut -d':' -f1)
  routing_key=$(echo $binding | cut -d':' -f2)
  
  curl -u $RABBITMQ_USER:$RABBITMQ_PASS -X POST \
    http://$RABBITMQ_HOST:$RABBITMQ_PORT/api/bindings/$RABBITMQ_VHOST/e/todo.events/q/$queue \
    -H "Content-Type: application/json" \
    -d '{"routing_key":"'$routing_key'"}'
done

echo "RabbitMQ setup completed!"