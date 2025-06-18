package api

import (
    "context"
    "user-service/users"

    "github.com/go-kit/kit/endpoint"
)

// Request/Response types
type registerRequest struct {
    Username  string `json:"username"`
    Password  string `json:"password"`
    Email     string `json:"email"`
    FirstName string `json:"firstName"`
    LastName  string `json:"lastName"`
}

type loginRequest struct {
    Username string `json:"username"`
    Password string `json:"password"`
}

type updatePreferencesRequest struct {
    TodoPrefs         users.TodoPrefs         `json:"todoPrefs"`
    NotificationPrefs users.NotificationPrefs `json:"notificationPrefs"`
}

type userResponse struct {
    User users.User `json:"user,omitempty"`
    Err  string     `json:"error,omitempty"`
}

type usersResponse struct {
    Users []users.User `json:"users,omitempty"`
    Err   string       `json:"error,omitempty"`
}

type statusResponse struct {
    Status bool   `json:"status"`
    Err    string `json:"error,omitempty"`
}

type statsResponse struct {
    Stats *users.UserStats `json:"stats,omitempty"`
    Err   string           `json:"error,omitempty"`
}

// --- Endpoint Makers ---

func makeRegisterEndpoint(svc TodoUserService) endpoint.Endpoint {
    return func(ctx context.Context, request interface{}) (interface{}, error) {
        req := request.(registerRequest)
        user, err := svc.Register(ctx, req.Username, req.Password, req.Email, req.FirstName, req.LastName)
        if err != nil {
            return userResponse{User: users.User{}, Err: err.Error()}, nil
        }
        return userResponse{User: *user, Err: ""}, nil
    }
}

func makeLoginEndpoint(svc TodoUserService) endpoint.Endpoint {
    return func(ctx context.Context, request interface{}) (interface{}, error) {
        req := request.(loginRequest)
        user, err := svc.Login(ctx, req.Username, req.Password)
        if err != nil {
            return userResponse{User: users.User{}, Err: err.Error()}, nil
        }
        return userResponse{User: *user, Err: ""}, nil
    }
}

func makeGetUserEndpoint(svc TodoUserService) endpoint.Endpoint {
    return func(ctx context.Context, request interface{}) (interface{}, error) {
        id := request.(string)
        user, err := svc.GetUser(ctx, id)
        if err != nil {
            return userResponse{User: users.User{}, Err: err.Error()}, nil
        }
        return userResponse{User: *user, Err: ""}, nil
    }
}

func makeGetUsersEndpoint(svc TodoUserService) endpoint.Endpoint {
    return func(ctx context.Context, request interface{}) (interface{}, error) {
        usersList, err := svc.GetUsers(ctx)
        if err != nil {
            return usersResponse{Users: nil, Err: err.Error()}, nil
        }
        return usersResponse{Users: usersList, Err: ""}, nil
    }
}

func makeUpdatePreferencesEndpoint(svc TodoUserService) endpoint.Endpoint {
    return func(ctx context.Context, request interface{}) (interface{}, error) {
        req := request.(struct {
            UserID            string
            TodoPrefs         users.TodoPrefs
            NotificationPrefs users.NotificationPrefs
        })
        err := svc.UpdatePreferences(ctx, req.UserID, req.TodoPrefs, req.NotificationPrefs)
        if err != nil {
            return statusResponse{Status: false, Err: err.Error()}, nil
        }
        return statusResponse{Status: true, Err: ""}, nil
    }
}

func makeGetUserStatsEndpoint(svc TodoUserService) endpoint.Endpoint {
    return func(ctx context.Context, request interface{}) (interface{}, error) {
        id := request.(string)
        stats, err := svc.GetUserStats(ctx, id)
        if err != nil {
            return statsResponse{Stats: nil, Err: err.Error()}, nil
        }
        return statsResponse{Stats: stats, Err: ""}, nil
    }
}
