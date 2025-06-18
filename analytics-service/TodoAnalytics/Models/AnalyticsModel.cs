using System.ComponentModel.DataAnnotations;

namespace TodoAnalytics.Models
{
    public class TaskEvent
    {
        public string EventType { get; set; } = string.Empty;
        public string UserId { get; set; } = string.Empty;
        public string? TaskId { get; set; }
        public string? ProjectId { get; set; }
        public DateTime Timestamp { get; set; }
        public Dictionary<string, object> Metadata { get; set; } = new();
    }

    public class UserProductivityMetrics
    {
        public string UserId { get; set; } = string.Empty;
        public int TasksCompleted { get; set; }
        public int TasksCreated { get; set; }
        public double AverageCompletionTime { get; set; }
        public string ProductivityScore { get; set; } = string.Empty;
        public DateTime PeriodStart { get; set; }
        public DateTime PeriodEnd { get; set; }
    }

    public class ProjectProgressMetrics
    {
        public string ProjectId { get; set; } = string.Empty;
        public string ProjectName { get; set; } = string.Empty;
        public int TotalTasks { get; set; }
        public int CompletedTasks { get; set; }
        public int InProgressTasks { get; set; }
        public int TodoTasks { get; set; }
        public double CompletionPercentage { get; set; }
        public DateTime LastUpdated { get; set; }
    }

    public class TaskCompletionRate
    {
        public DateTime Date { get; set; }
        public int TotalTasks { get; set; }
        public int CompletedTasks { get; set; }
        public double CompletionRate { get; set; }
    }

    public class AnalyticsEventRequest
    {
        [Required]
        public string Event { get; set; } = string.Empty;
        
        [Required]
        public string UserId { get; set; } = string.Empty;
        
        public string? TaskId { get; set; }
        public string? ProjectId { get; set; }
        public DateTime? Timestamp { get; set; }
        public Dictionary<string, object>? Metadata { get; set; }
    }
}
