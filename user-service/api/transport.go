package api

import (
    "context"
    "encoding/json"
    "net/http"
    "user-service/users"

    "github.com/gorilla/mux"
    httptransport "github.com/go-kit/kit/transport/http"
    "github.com/go-kit/kit/log"
)

// HTTP Handlers
func MakeRegisterHandler(svc TodoUserService, logger log.Logger) http.Handler {
    return httptransport.NewServer(
        makeRegisterEndpoint(svc),
        decodeRegisterRequest,
        encodeResponse,
    )
}

func MakeLoginHandler(svc TodoUserService, logger log.Logger) http.Handler {
    return httptransport.NewServer(
        makeLoginEndpoint(svc),
        decodeLoginRequest,
        encodeResponse,
    )
}

func MakeGetUserHandler(svc TodoUserService, logger log.Logger) http.Handler {
    return httptransport.NewServer(
        makeGetUserEndpoint(svc),
        decodeGetUserRequest,
        encodeResponse,
    )
}

func MakeGetUsersHandler(svc TodoUserService, logger log.Logger) http.Handler {
    return httptransport.NewServer(
        makeGetUsersEndpoint(svc),
        decodeGetUsersRequest,
        encodeResponse,
    )
}

func MakeUpdatePreferencesHandler(svc TodoUserService, logger log.Logger) http.Handler {
    return httptransport.NewServer(
        makeUpdatePreferencesEndpoint(svc),
        decodeUpdatePreferencesRequest,
        encodeResponse,
    )
}

func MakeGetUserStatsHandler(svc TodoUserService, logger log.Logger) http.Handler {
    return httptransport.NewServer(
        makeGetUserStatsEndpoint(svc),
        decodeGetUserStatsRequest,
        encodeResponse,
    )
}

// Decoders
func decodeRegisterRequest(_ context.Context, r *http.Request) (interface{}, error) {
    var req registerRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        return nil, err
    }
    return req, nil
}

func decodeLoginRequest(_ context.Context, r *http.Request) (interface{}, error) {
    var req loginRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        return nil, err
    }
    return req, nil
}

func decodeGetUserRequest(_ context.Context, r *http.Request) (interface{}, error) {
    vars := mux.Vars(r)
    return vars["id"], nil
}

func decodeGetUsersRequest(_ context.Context, r *http.Request) (interface{}, error) {
    return nil, nil
}

func decodeUpdatePreferencesRequest(_ context.Context, r *http.Request) (interface{}, error) {
    vars := mux.Vars(r)
    userID := vars["id"]
    
    var req updatePreferencesRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        return nil, err
    }
    
    return struct {
        UserID            string
        TodoPrefs         users.TodoPrefs
        NotificationPrefs users.NotificationPrefs
    }{
        UserID:            userID,
        TodoPrefs:         req.TodoPrefs,
        NotificationPrefs: req.NotificationPrefs,
    }, nil
}

func decodeGetUserStatsRequest(_ context.Context, r *http.Request) (interface{}, error) {
    vars := mux.Vars(r)
    return vars["id"], nil
}

// Response encoder
func encodeResponse(_ context.Context, w http.ResponseWriter, response interface{}) error {
    w.Header().Set("Content-Type", "application/json; charset=utf-8")
    return json.NewEncoder(w).Encode(response)
}