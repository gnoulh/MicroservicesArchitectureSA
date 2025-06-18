package main

import (
    "context"
    "log"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"
    
    "github.com/gorilla/mux"
    "github.com/go-kit/kit/log"
    "gopkg.in/mgo.v2"
    "go.mongodb.org/mongo-driver/mongo"
    "go.mongodb.org/mongo-driver/mongo/options"
    
    "user-service/internal/consul"
    "user-service/internal/health"
    "user-service/internal/handlers"

    "user-service/api"
    "user-service/db/mongodb"
)

func main() {
    // Logger
    var logger log.Logger
    logger = log.NewLogfmtLogger(os.Stderr)
    logger = log.With(logger, "ts", log.DefaultTimestampUTC)
    logger = log.With(logger, "caller", log.DefaultCaller)
    
    // MongoDB connection
    mongoURL := getEnv("MONGO_URL", "mongodb://localhost:27017/todoapp")
    session, err := mgo.Dial(mongoURL)
    if err != nil {
        logger.Log("error", "Failed to connect to MongoDB", "err", err)
        os.Exit(1)
    }
    defer session.Close()
    
    // Repository and service
    repository := mongodb.NewMongoRepository(session)
    service := api.NewTodoUserService(repository)
    
    // HTTP router
    router := mux.NewRouter()
    
    // Todo-focused API endpoints
    router.Handle("/register", api.MakeRegisterHandler(service, logger)).Methods("POST")
    router.Handle("/login", api.MakeLoginHandler(service, logger)).Methods("POST")
    router.Handle("/users", api.MakeGetUsersHandler(service, logger)).Methods("GET")
    router.Handle("/users/{id}", api.MakeGetUserHandler(service, logger)).Methods("GET")
    router.Handle("/users/{id}/preferences", api.MakeUpdatePreferencesHandler(service, logger)).Methods("PUT")
    router.Handle("/users/{id}/stats", api.MakeGetUserStatsHandler(service, logger)).Methods("GET")
    
    // Health check
    router.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
        w.Write([]byte("OK"))
    }).Methods("GET")
    
    // Start server
    port := getEnv("PORT", "8084")
    logger.Log("msg", "Todo User Service starting", "port", port)
    
    if err := http.ListenAndServe(":"+port, router); err != nil {
        logger.Log("error", "Server failed to start", "err", err)
        os.Exit(1)
    }
}

func getEnv(key, defaultValue string) string {
    if value := os.Getenv(key); value != "" {
        return value
    }
    return defaultValue
}