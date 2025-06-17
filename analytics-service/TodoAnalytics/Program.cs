using TodoAnalytics.Models;
using TodoAnalytics.Services;
using Serilog;

// Configure Serilog
Log.Logger = new LoggerConfiguration()
    .WriteTo.Console()
    .CreateLogger();

var builder = WebApplication.CreateBuilder(args);

// Add Serilog
builder.Host.UseSerilog();

// Add services to the container.
// Learn more about configuring OpenAPI at https://aka.ms/aspnet/openapi
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Configure InfluxDB
builder.Services.Configure<InfluxDBConfig>(
    builder.Configuration.GetSection("InfluxDB"));
builder.Services.AddSingleton<IInfluxDBService, InfluxDBService>();

// Configure CORS
builder.Services.AddCors(options =>
{
    options.AddPolicy("TodoPolicy", policy =>
    {
        var allowedOrigins = builder.Configuration.GetSection("Cors:AllowedOrigins").Get<string[]>() ?? [];
        policy.WithOrigins(allowedOrigins)
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

builder.WebHost.UseUrls("http://+:8088");

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors("TodoPolicy");
app.UseRouting();
app.MapControllers();

app.Run();
