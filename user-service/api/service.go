package api

import (
    "context"
    "errors"
    "time"
    
    "user-service/users"
)

// TodoUserService interface
type TodoUserService interface {
    // Basic user operations
    Register(ctx context.Context, username, password, email, firstName, lastName string) (*users.User, error)
    Login(ctx context.Context, username, password string) (*users.User, error)
    GetUser(ctx context.Context, userID string) (*users.User, error)
    GetUsers(ctx context.Context) ([]users.User, error)
    UpdateUser(ctx context.Context, user *users.User) error
    DeleteUser(ctx context.Context, userID string) error
    
    // Todo-specific operations
    UpdatePreferences(ctx context.Context, userID string, todoPrefs users.TodoPrefs, notifPrefs users.NotificationPrefs) error
    GetUserStats(ctx context.Context, userID string) (*users.UserStats, error)
    UpdateTimezone(ctx context.Context, userID, timezone string) error
    UpdateDefaultProject(ctx context.Context, userID, projectID string) error
}

type service struct {
    repository users.Repository
}

func NewTodoUserService(repo users.Repository) TodoUserService {
    return &service{repository: repo}
}

func (s *service) Register(ctx context.Context, username, password, email, firstName, lastName string) (*users.User, error) {
    // Check if user already exists
    if existingUser, _ := s.repository.GetUserByName(username); existingUser != nil {
        return nil, errors.New("username already exists")
    }
    
    user := users.NewUser(username, password, email, firstName, lastName)
    if err := user.Validate(); err != nil {
        return nil, err
    }
    
    // Hash password (implement proper hashing)
    hashedPassword, salt := hashPassword(password)
    user.Password = hashedPassword
    user.Salt = salt
    
    if err := s.repository.CreateUser(user); err != nil {
        return nil, err
    }
    
    // Don't return password
    user.Password = ""
    return user, nil
}

func (s *service) Login(ctx context.Context, username, password string) (*users.User, error) {
    user, err := s.repository.GetUserByName(username)
    if err != nil {
        return nil, errors.New("invalid credentials")
    }
    
    if !validatePassword(password, user.Password, user.Salt) {
        return nil, errors.New("invalid credentials")
    }
    
    // Don't return password
    user.Password = ""
    return user, nil
}

func (s *service) GetUser(ctx context.Context, userID string) (*users.User, error) {
    user, err := s.repository.GetUser(userID)
    if err != nil {
        return nil, err
    }
    user.Password = "" // Never return password
    return user, nil
}

func (s *service) GetUsers(ctx context.Context) ([]users.User, error) {
    users, err := s.repository.GetUsers()
    if err != nil {
        return nil, err
    }
    
    // Remove passwords from all users
    for i := range users {
        users[i].Password = ""
    }
    
    return users, nil
}

func (s *service) UpdateUser(ctx context.Context, user *users.User) error {
    user.UpdatedAt = time.Now()
    return s.repository.UpdateUser(user)
}

func (s *service) DeleteUser(ctx context.Context, userID string) error {
    return s.repository.DeleteUser(userID)
}

func (s *service) UpdatePreferences(ctx context.Context, userID string, todoPrefs users.TodoPrefs, notifPrefs users.NotificationPrefs) error {
    return s.repository.UpdateUserPreferences(userID, todoPrefs, notifPrefs)
}

func (s *service) GetUserStats(ctx context.Context, userID string) (*users.UserStats, error) {
    return s.repository.GetUserStats(userID)
}

func (s *service) UpdateTimezone(ctx context.Context, userID, timezone string) error {
    user, err := s.repository.GetUser(userID)
    if err != nil {
        return err
    }
    
    user.Timezone = timezone
    user.UpdatedAt = time.Now()
    
    return s.repository.UpdateUser(user)
}

func (s *service) UpdateDefaultProject(ctx context.Context, userID, projectID string) error {
    user, err := s.repository.GetUser(userID)
    if err != nil {
        return err
    }
    
    user.DefaultProjectID = projectID
    user.UpdatedAt = time.Now()
    
    return s.repository.UpdateUser(user)
}

// Simple password hashing (implement proper bcrypt in production)
func hashPassword(password string) (string, string) {
    // This is a simplified version - use bcrypt in production
    salt := "randomsalt" // Generate random salt
    return password + salt, salt // Simplified hash
}

func validatePassword(password, hashedPassword, salt string) bool {
    return hashedPassword == password+salt // Simplified validation
}