package rabbitmq

import (
    "encoding/json"
    "fmt"
    "log"
    "time"

    "github.com/google/uuid"
    "github.com/streadway/amqp"
)

type Publisher struct {
    conn    *amqp.Connection
    channel *amqp.Channel
    exchange string
}

type BaseEvent struct {
    EventID   string      `json:"eventId"`
    Timestamp string      `json:"timestamp"`
    EventType string      `json:"eventType"`
    Version   string      `json:"version"`
    Data      interface{} `json:"data"`
}

func NewPublisher() (*Publisher, error) {
    conn, err := amqp.Dial("amqp://todouser:todopass123@localhost:5672/todo_vhost")
    if err != nil {
        return nil, fmt.Errorf("failed to connect to RabbitMQ: %v", err)
    }

    ch, err := conn.Channel()
    if err != nil {
        return nil, fmt.Errorf("failed to open channel: %v", err)
    }

    err = ch.ExchangeDeclare(
        "todo.events", // name
        "topic",       // type
        true,          // durable
        false,         // auto-deleted
        false,         // internal
        false,         // no-wait
        nil,           // arguments
    )
    if err != nil {
        return nil, fmt.Errorf("failed to declare exchange: %v", err)
    }

    return &Publisher{
        conn:     conn,
        channel:  ch,
        exchange: "todo.events",
    }, nil
}

func (p *Publisher) PublishUserRegistered(userID, username, email string) error {
    event := BaseEvent{
        EventID:   uuid.New().String(),
        Timestamp: time.Now().Format(time.RFC3339),
        EventType: "user.registered",
        Version:   "1.0",
        Data: map[string]interface{}{
            "userId":           userID,
            "username":         username,
            "email":            email,
            "registrationDate": time.Now().Format(time.RFC3339),
        },
    }

    return p.publish("user.registered", event)
}

func (p *Publisher) publish(routingKey string, event BaseEvent) error {
    body, err := json.Marshal(event)
    if err != nil {
        return fmt.Errorf("failed to marshal event: %v", err)
    }

    err = p.channel.Publish(
        p.exchange,  // exchange
        routingKey,  // routing key
        false,       // mandatory
        false,       // immediate
        amqp.Publishing{
            ContentType: "application/json",
            Body:        body,
            Persistent:  true,
        },
    )
    if err != nil {
        return fmt.Errorf("failed to publish message: %v", err)
    }

    log.Printf("Published event: %s", routingKey)
    return nil
}

func (p *Publisher) Close() error {
    if p.channel != nil {
        p.channel.Close()
    }
    if p.conn != nil {
        return p.conn.Close()
    }
    return nil
}