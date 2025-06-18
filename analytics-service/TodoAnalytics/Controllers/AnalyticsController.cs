using Microsoft.AspNetCore.Mvc;
using TodoAnalytics.Models;
using TodoAnalytics.Services;

namespace TodoAnalytics.Controllers
{
    [ApiController]
    [Route("analytics")]
    public class AnalyticsController : ControllerBase
    {
        private readonly IInfluxDBService _influxDBService;
        private readonly ILogger<AnalyticsController> _logger;

        public AnalyticsController(IInfluxDBService influxDBService, ILogger<AnalyticsController> logger)
        {
            _influxDBService = influxDBService;
            _logger = logger;
        }

        [HttpGet("user/{userId}/productivity")]
        public async Task<ActionResult<List<UserProductivityMetrics>>> GetUserProductivity(
            string userId,
            [FromQuery] DateTime? start = null,
            [FromQuery] DateTime? end = null)
        {
            try
            {
                var startDate = start ?? DateTime.UtcNow.AddDays(-30);
                var endDate = end ?? DateTime.UtcNow;

                var metrics = await _influxDBService.GetUserProductivityAsync(userId, startDate, endDate);
                return Ok(metrics);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting user productivity for {UserId}", userId);
                return StatusCode(500, "Internal server error");
            }
        }

        [HttpGet("project/{projectId}/progress")]
        public async Task<ActionResult<ProjectProgressMetrics>> GetProjectProgress(string projectId)
        {
            try
            {
                var metrics = await _influxDBService.GetProjectProgressAsync(projectId);
                return Ok(metrics);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting project progress for {ProjectId}", projectId);
                return StatusCode(500, "Internal server error");
            }
        }

        [HttpGet("tasks/completion-rate")]
        public async Task<ActionResult<List<TaskCompletionRate>>> GetTaskCompletionRate(
            [FromQuery] DateTime? start = null,
            [FromQuery] DateTime? end = null)
        {
            try
            {
                var startDate = start ?? DateTime.UtcNow.AddDays(-30);
                var endDate = end ?? DateTime.UtcNow;

                var rates = await _influxDBService.GetTaskCompletionRateAsync(startDate, endDate);
                return Ok(rates);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting task completion rate");
                return StatusCode(500, "Internal server error");
            }
        }

        [HttpPost("events")]
        public async Task<ActionResult> PostEvent([FromBody] AnalyticsEventRequest request)
        {
            try
            {
                if (!ModelState.IsValid)
                    return BadRequest(ModelState);

                var taskEvent = new TaskEvent
                {
                    EventType = request.Event,
                    UserId = request.UserId,
                    TaskId = request.TaskId,
                    ProjectId = request.ProjectId,
                    Timestamp = request.Timestamp ?? DateTime.UtcNow,
                    Metadata = request.Metadata ?? new Dictionary<string, object>()
                };

                await _influxDBService.WriteEventAsync(taskEvent);
                
                return Ok(new { message = "Event recorded successfully" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error posting analytics event");
                return StatusCode(500, "Internal server error");
            }
        }

        [HttpGet("health")]
        public ActionResult GetHealth()
        {
            return Ok(new { status = "healthy", timestamp = DateTime.UtcNow });
        }
    }
}