package health

import (
    "context"
    "encoding/json"
    "net/http"
    "time"
    
    "go.mongodb.org/mongo-driver/mongo"
    "go.mongodb.org/mongo-driver/mongo/readpref"
)

type HealthChecker struct {
    db *mongo.Database
}

type HealthResponse struct {
    Status    string            `json:"status"`
    Timestamp time.Time         `json:"timestamp"`
    Checks    map[string]string `json:"checks"`
}

func NewHealthChecker(db *mongo.Database) *HealthChecker {
    return &HealthChecker{db: db}
}

func (h *HealthChecker) LivenessHandler(w http.ResponseWriter, r *http.Request) {
    response := HealthResponse{
        Status:    "UP",
        Timestamp: time.Now(),
        Checks:    make(map[string]string),
    }
    
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(response)
}

func (h *HealthChecker) ReadinessHandler(w http.ResponseWriter, r *http.Request) {
    response := HealthResponse{
        Status:    "UP",
        Timestamp: time.Now(),
        Checks:    make(map[string]string),
    }
    
    // Check database connectivity
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()
    
    if err := h.db.Client().Ping(ctx, readpref.Primary()); err != nil {
        response.Status = "DOWN"
        response.Checks["database"] = "FAIL: " + err.Error()
        w.WriteHeader(http.StatusServiceUnavailable)
    } else {
        response.Checks["database"] = "OK"
    }
    
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(response)
}

func (h *HealthChecker) HealthHandler(w http.ResponseWriter, r *http.Request) {
    h.ReadinessHandler(w, r)
}