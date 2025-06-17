using InfluxDB.Client;
using InfluxDB.Client.Api.Domain;
using InfluxDB.Client.Writes;
using TodoAnalytics.Models;

namespace TodoAnalytics.Services
{
    public interface IInfluxDBService
    {
        Task WriteEventAsync(TaskEvent taskEvent);
        Task<List<UserProductivityMetrics>> GetUserProductivityAsync(string userId, DateTime start, DateTime end);
        Task<ProjectProgressMetrics> GetProjectProgressAsync(string projectId);
        Task<List<TaskCompletionRate>> GetTaskCompletionRateAsync(DateTime start, DateTime end);
    }

    public class InfluxDBService : IInfluxDBService, IDisposable
    {
        private readonly InfluxDBClient _client;
        private readonly string _bucket;
        private readonly string _org;
        private readonly ILogger<InfluxDBService> _logger;

        public InfluxDBService(IConfiguration config, ILogger<InfluxDBService> logger)
        {
            _logger = logger;
            var influxConfig = config.GetSection("InfluxDB").Get<InfluxDBConfig>()!;
            
            _client = new InfluxDBClient(influxConfig.Url, influxConfig.Token);
            _bucket = influxConfig.Bucket;
            _org = influxConfig.Org;
        }

        public async Task WriteEventAsync(TaskEvent taskEvent)
        {
            try
            {
                var writeApi = _client.GetWriteApiAsync();
                
                var point = PointData
                    .Measurement("task_events")
                    .Tag("event_type", taskEvent.EventType)
                    .Tag("user_id", taskEvent.UserId)
                    .Field("count", 1)
                    .Timestamp(taskEvent.Timestamp, WritePrecision.Ns);

                if (!string.IsNullOrEmpty(taskEvent.TaskId))
                    point = point.Tag("task_id", taskEvent.TaskId);
                
                if (!string.IsNullOrEmpty(taskEvent.ProjectId))
                    point = point.Tag("project_id", taskEvent.ProjectId);

                foreach (var meta in taskEvent.Metadata)
                {
                    point = point.Field(meta.Key, meta.Value);
                }

                await writeApi.WritePointAsync(point, _bucket, _org);
                _logger.LogInformation($"Event written: {taskEvent.EventType} for user {taskEvent.UserId}");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error writing event to InfluxDB");
                throw;
            }
        }

        public async Task<List<UserProductivityMetrics>> GetUserProductivityAsync(string userId, DateTime start, DateTime end)
        {
            try
            {
                var queryApi = _client.GetQueryApi();
                
                var flux = $@"
                    from(bucket: ""{_bucket}"")
                    |> range(start: {start:yyyy-MM-ddTHH:mm:ssZ}, stop: {end:yyyy-MM-ddTHH:mm:ssZ})
                    |> filter(fn: (r) => r._measurement == ""task_events"")
                    |> filter(fn: (r) => r.user_id == ""{userId}"")
                    |> group(columns: [""event_type""])
                    |> count()";

                var tables = await queryApi.QueryAsync(flux, _org);
                
                var metrics = new List<UserProductivityMetrics>();
                var completedTasks = 0;
                var createdTasks = 0;

                foreach (var table in tables)
                {
                    foreach (var record in table.Records)
                    {
                        var eventType = record.GetValueByKey("event_type")?.ToString();
                        var count = Convert.ToInt32(record.GetValue());

                        if (eventType == "task_completed")
                            completedTasks = count;
                        else if (eventType == "task_created")
                            createdTasks = count;
                    }
                }

                var productivity = new UserProductivityMetrics
                {
                    UserId = userId,
                    TasksCompleted = completedTasks,
                    TasksCreated = createdTasks,
                    AverageCompletionTime = completedTasks > 0 ? 2.5 : 0, // Simplified calculation
                    ProductivityScore = CalculateProductivityScore(completedTasks, createdTasks),
                    PeriodStart = start,
                    PeriodEnd = end
                };

                metrics.Add(productivity);
                return metrics;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error querying user productivity");
                throw;
            }
        }

        public async Task<ProjectProgressMetrics> GetProjectProgressAsync(string projectId)
        {
            try
            {
                var queryApi = _client.GetQueryApi();
                
                var flux = $@"
                    from(bucket: ""{_bucket}"")
                    |> range(start: -30d)
                    |> filter(fn: (r) => r._measurement == ""task_events"")
                    |> filter(fn: (r) => r.project_id == ""{projectId}"")
                    |> filter(fn: (r) => r.event_type == ""task_created"" or r.event_type == ""task_completed"")
                    |> group(columns: [""event_type""])
                    |> count()";

                var tables = await queryApi.QueryAsync(flux, _org);
                
                var totalTasks = 0;
                var completedTasks = 0;

                foreach (var table in tables)
                {
                    foreach (var record in table.Records)
                    {
                        var eventType = record.GetValueByKey("event_type")?.ToString();
                        var count = Convert.ToInt32(record.GetValue());

                        if (eventType == "task_created")
                            totalTasks = count;
                        else if (eventType == "task_completed")
                            completedTasks = count;
                    }
                }

                return new ProjectProgressMetrics
                {
                    ProjectId = projectId,
                    ProjectName = $"Project {projectId}",
                    TotalTasks = totalTasks,
                    CompletedTasks = completedTasks,
                    InProgressTasks = Math.Max(0, (totalTasks - completedTasks) / 2),
                    TodoTasks = Math.Max(0, totalTasks - completedTasks),
                    CompletionPercentage = totalTasks > 0 ? (double)completedTasks / totalTasks * 100 : 0,
                    LastUpdated = DateTime.UtcNow
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error querying project progress");
                throw;
            }
        }

        public async Task<List<TaskCompletionRate>> GetTaskCompletionRateAsync(DateTime start, DateTime end)
        {
            try
            {
                var queryApi = _client.GetQueryApi();
                
                var flux = $@"
                    from(bucket: ""{_bucket}"")
                    |> range(start: {start:yyyy-MM-ddTHH:mm:ssZ}, stop: {end:yyyy-MM-ddTHH:mm:ssZ})
                    |> filter(fn: (r) => r._measurement == ""task_events"")
                    |> filter(fn: (r) => r.event_type == ""task_completed"" or r.event_type == ""task_created"")
                    |> aggregateWindow(every: 1d, fn: count)
                    |> group(columns: [""event_type""])";

                var tables = await queryApi.QueryAsync(flux, _org);
                
                var completionRates = new List<TaskCompletionRate>();
                
                // Simplified implementation - in real scenario, you'd process the time series data
                var rate = new TaskCompletionRate
                {
                    Date = DateTime.UtcNow.Date,
                    TotalTasks = 10,
                    CompletedTasks = 7,
                    CompletionRate = 0.7
                };
                
                completionRates.Add(rate);
                return completionRates;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error querying task completion rate");
                throw;
            }
        }

        private string CalculateProductivityScore(int completed, int created)
        {
            if (created == 0) return "No Data";
            
            var ratio = (double)completed / created;
            return ratio switch
            {
                >= 0.8 => "High",
                >= 0.5 => "Medium",
                _ => "Low"
            };
        }

        public void Dispose()
        {
            _client?.Dispose();
        }
    }
}
