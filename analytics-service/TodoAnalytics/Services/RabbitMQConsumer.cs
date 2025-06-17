using System;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;

namespace AnalyticsService.Services
{
    public class RabbitMQConsumer : BackgroundService
    {
        private readonly ILogger<RabbitMQConsumer> _logger;
        private readonly IServiceProvider _serviceProvider;
        private IConnection _connection;
        private IModel _channel;
        private const string ExchangeName = "todo.events";
        private const string QueueName = "analytics.queue";

        public RabbitMQConsumer(ILogger<RabbitMQConsumer> logger, IServiceProvider serviceProvider)
        {
            _logger = logger;
            _serviceProvider = serviceProvider;
            InitializeRabbitMQ();
        }

        private void InitializeRabbitMQ()
        {
            var factory = new ConnectionFactory()
            {
                HostName = "localhost",
                Port = 5672,
                UserName = "todouser",
                Password = "todopass123",
                VirtualHost = "todo_vhost"
            };

            _connection = factory.CreateConnection();
            _channel = _connection.CreateModel();

            _channel.ExchangeDeclare(exchange: ExchangeName, type: ExchangeType.Topic, durable: true);
            _channel.QueueDeclare(queue: QueueName, durable: true, exclusive: false, autoDelete: false);

            // Bind to routing keys
            string[] routingKeys = { "task.*", "project.*", "user.*" };
            foreach (var routingKey in routingKeys)
            {
                _channel.QueueBind(queue: QueueName, exchange: ExchangeName, routingKey: routingKey);
            }

            _logger.LogInformation("RabbitMQ connection initialized for analytics service");
        }

        protected override Task ExecuteAsync(CancellationToken stoppingToken)
        {
            stoppingToken.ThrowIfCancellationRequested();

            var consumer = new EventingBasicConsumer(_channel);
            consumer.Received += async (ch, ea) =>
            {
                try
                {
                    var content = Encoding.UTF8.GetString(ea.Body.ToArray());
                    var message = JsonSerializer.Deserialize<EventMessage>(content);

                    _logger.LogInformation($"Received analytics event: {message.EventType}");

                    using (var scope = _serviceProvider.CreateScope())
                    {
                        var analyticsService = scope.ServiceProvider.GetRequiredService<IAnalyticsService>();
                        await ProcessEvent(analyticsService, message);
                    }

                    _channel.BasicAck(ea.DeliveryTag, false);
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Error processing analytics message");
                    _channel.BasicNack(ea.DeliveryTag, false, true);
                }
            };

            _channel.BasicConsume(queue: QueueName, autoAck: false, consumer: consumer);

            return Task.CompletedTask;
        }

        private async Task ProcessEvent(IAnalyticsService analyticsService, EventMessage message)
        {
            switch (message.EventType)
            {
                case "task.created":
                    await analyticsService.RecordTaskCreated(message);
                    break;
                case "task.completed":
                    await analyticsService.RecordTaskCompleted(message);
                    break;
                case "task.updated":
                    await analyticsService.RecordTaskUpdated(message);
                    break;
                case "project.created":
                    await analyticsService.RecordProjectCreated(message);
                    break;
                case "user.registered":
                    await analyticsService.RecordUserRegistered(message);
                    break;
                default:
                    _logger.LogWarning($"Unknown event type: {message.EventType}");
                    break;
            }
        }

        public override void Dispose()
        {
            _channel?.Close();
            _connection?.Close();
            base.Dispose();
        }
    }

    public class EventMessage
    {
        public string EventId { get; set; }
        public DateTime Timestamp { get; set; }
        public string EventType { get; set; }
        public string Version { get; set; }
        public JsonElement Data { get; set; }
    }
}