# Start from official Golang image
FROM golang:1.24-alpine AS builder

WORKDIR /app

# Copy go.mod and go.sum and download dependencies
COPY go.mod go.sum ./
RUN go mod download

# Copy the source code
COPY . .

# Build the Go binary
RUN go build -o user-service .

# Final image
FROM alpine:latest

WORKDIR /app

# Copy the binary from builder
COPY --from=builder /app/user-service .

# Expose the port that service listens on
EXPOSE 8084

# Command to run
ENTRYPOINT ["./user-service"]
