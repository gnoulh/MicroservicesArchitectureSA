#!/bin/bash

echo "=== Preparing Service Mesh Integration ==="

# Create Consul Connect configuration
mkdir -p ./consul-connect

# Consul Connect configuration
cat > ./consul-connect/consul-connect.hcl << 'EOF'
# Consul Connect configuration
connect {
  enabled = true
}

ports {
  grpc = 8502
}

ui_config {
  enabled = true
}
EOF

# Update docker-compose for Consul Connect
cat > ./consul-connect/docker-compose.connect.yml << 'EOF'
version: '3.8'
services:
  consul:
    image: consul:1.15.3
    container_name: consul
    ports:
      - "8500:8500"
      - "8502:8502"
      - "8600:8600/udp"
    command: >
      consul agent -server -ui -node=server-1 -bootstrap-expect=1
      -client=0.0.0.0 -datacenter=dc1 -config-file=/consul/config/consul-connect.hcl
    volumes:
      - ./consul-connect/consul-connect.hcl:/consul/config/consul-connect.hcl
      - consul_data:/consul/data
    networks:
      - microservices-network

  # Envoy sidecars for each service
  user-service-sidecar:
    image: envoyproxy/envoy:v1.27-latest
    container_name: user-service-sidecar
    depends_on:
      - consul
      - user-service
    networks:
      - microservices-network
    command: >
      envoy -c /etc/envoy/envoy.yaml
    volumes:
      - ./consul-connect/envoy-user-service.yaml:/etc/envoy/envoy.yaml

  task-service-sidecar:
    image: envoyproxy/envoy:v1.27-latest
    container_name: task-service-sidecar
    depends_on:
      - consul
      - task-service
    networks:
      - microservices-network
    command: >
      envoy -c /etc/envoy/envoy.yaml
    volumes:
      - ./consul-connect/envoy-task-service.yaml:/etc/envoy/envoy.yaml

volumes:
  consul_data:

networks:
  microservices-network:
    driver: bridge
EOF

echo "Service mesh configuration created in ./consul-connect/"