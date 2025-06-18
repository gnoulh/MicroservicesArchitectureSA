package users

import (
    "time"
    "errors"
)

// User struct for Todo application
type User struct {
    UserID    string    `bson:"_id,omitempty" json:"id"`
    Username  string    `bson:"username" json:"username"`
    Email     string    `bson:"email" json:"email"`
    FirstName string    `bson:"firstName,omitempty" json:"firstName,omitempty"`
    LastName  string    `bson:"lastName,omitempty" json:"lastName,omitempty"`
    Password  string    `bson:"password,omitempty" json:"-"` // Never return password in JSON
    Salt      string    `bson:"salt" json:"-"`
    
    // Todo-specific fields
    DefaultProjectID       string                 `bson:"defaultProjectId,omitempty" json:"defaultProjectId,omitempty"`
    NotificationPrefs      NotificationPrefs      `bson:"notificationPrefs,omitempty" json:"notificationPrefs,omitempty"`
    TodoPrefs              TodoPrefs              `bson:"todoPrefs,omitempty" json:"todoPrefs,omitempty"`
    Timezone               string                 `bson:"timezone,omitempty" json:"timezone,omitempty"`
    
    // Timestamps
    CreatedAt time.Time `bson:"createdAt" json:"createdAt"`
    UpdatedAt time.Time `bson:"updatedAt" json:"updatedAt"`
}

// Todo-specific preference structures
type NotificationPrefs struct {
    EmailEnabled       bool `bson:"emailEnabled" json:"emailEnabled"`
    PushEnabled        bool `bson:"pushEnabled" json:"pushEnabled"`
    DailyDigest        bool `bson:"dailyDigest" json:"dailyDigest"`
    TaskDueReminders   bool `bson:"taskDueReminders" json:"taskDueReminders"`
    ProjectUpdates     bool `bson:"projectUpdates" json:"projectUpdates"`
    WeeklyReport       bool `bson:"weeklyReport" json:"weeklyReport"`
}

type TodoPrefs struct {
    DefaultDueTime       string `bson:"defaultDueTime,omitempty" json:"defaultDueTime,omitempty"` // "09:00"
    AutoArchiveCompleted bool   `bson:"autoArchiveCompleted" json:"autoArchiveCompleted"`
    ShowCompletedTasks   bool   `bson:"showCompletedTasks" json:"showCompletedTasks"`
    DefaultPriority      string `bson:"defaultPriority,omitempty" json:"defaultPriority,omitempty"` // "low", "medium", "high"
    WeekStartsOn         int    `bson:"weekStartsOn" json:"weekStartsOn"` // 0=Sunday, 1=Monday
    TasksPerPage         int    `bson:"tasksPerPage" json:"tasksPerPage"`
}

// User creation
func NewUser(username, password, email, firstName, lastName string) *User {
    return &User{
        Username:  username,
        Email:     email,
        FirstName: firstName,
        LastName:  lastName,
        Password:  password,
        Timezone:  "UTC",
        CreatedAt: time.Now(),
        UpdatedAt: time.Now(),
        // Default preferences
        NotificationPrefs: NotificationPrefs{
            EmailEnabled:     true,
            PushEnabled:      true,
            DailyDigest:      false,
            TaskDueReminders: true,
            ProjectUpdates:   true,
            WeeklyReport:     false,
        },
        TodoPrefs: TodoPrefs{
            DefaultDueTime:       "09:00",
            AutoArchiveCompleted: false,
            ShowCompletedTasks:   true,
            DefaultPriority:      "medium",
            WeekStartsOn:         1, // Monday
            TasksPerPage:         50,
        },
    }
}

// Validation method
func (u *User) Validate() error {
    if u.Username == "" {
        return errors.New("username is required")
    }
    if u.Email == "" {
        return errors.New("email is required")
    }
    if u.Password == "" {
        return errors.New("password is required")
    }
    return nil
}

// Repository interface for user operations
type Repository interface {
    CreateUser(*User) error
    GetUser(string) (*User, error)
    GetUserByName(string) (*User, error)
    GetUsers() ([]User, error)
    UpdateUser(*User) error
    DeleteUser(string) error
    
    // Todo-specific methods
    UpdateUserPreferences(string, TodoPrefs, NotificationPrefs) error
    GetUserStats(string) (*UserStats, error)
}

// User statistics for todo application
type UserStats struct {
    UserID           string `json:"userId"`
    TotalTasks       int    `json:"totalTasks"`
    CompletedTasks   int    `json:"completedTasks"`
    PendingTasks     int    `json:"pendingTasks"`
    OverdueTasks     int    `json:"overdueTasks"`
    TotalProjects    int    `json:"totalProjects"`
    LastActivityDate string `json:"lastActivityDate"`
}