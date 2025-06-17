package mongodb

import (
    "time"
    "user-service/users"
    "gopkg.in/mgo.v2"
    "gopkg.in/mgo.v2/bson"
)

type MongoRepository struct {
    session *mgo.Session
}

func NewMongoRepository(session *mgo.Session) *MongoRepository {
    return &MongoRepository{session: session}
}

func (r *MongoRepository) CreateUser(user *users.User) error {
    c := r.session.DB("todoapp").C("users")
    
    // Generate ID if not provided
    if user.UserID == "" {
        user.UserID = bson.NewObjectId().Hex()
    }
    
    // Set timestamps
    user.CreatedAt = time.Now()
    user.UpdatedAt = time.Now()
    
    return c.Insert(user)
}

func (r *MongoRepository) GetUser(userID string) (*users.User, error) {
    c := r.session.DB("todoapp").C("users")
    
    var user users.User
    err := c.FindId(userID).One(&user)
    if err != nil {
        return nil, err
    }
    
    return &user, nil
}

func (r *MongoRepository) GetUserByName(username string) (*users.User, error) {
    c := r.session.DB("todoapp").C("users")
    
    var user users.User
    err := c.Find(bson.M{"username": username}).One(&user)
    if err != nil {
        return nil, err
    }
    
    return &user, nil
}

func (r *MongoRepository) GetUsers() ([]users.User, error) {
    c := r.session.DB("todoapp").C("users")
    
    var users []users.User
    err := c.Find(nil).All(&users)
    return users, err
}

func (r *MongoRepository) UpdateUser(user *users.User) error {
    c := r.session.DB("todoapp").C("users")
    
    user.UpdatedAt = time.Now()
    
    return c.UpdateId(user.UserID, user)
}

func (r *MongoRepository) DeleteUser(userID string) error {
    c := r.session.DB("todoapp").C("users")
    return c.RemoveId(userID)
}

func (r *MongoRepository) UpdateUserPreferences(userID string, todoPrefs users.TodoPrefs, notifPrefs users.NotificationPrefs) error {
    c := r.session.DB("todoapp").C("users")
    
    return c.UpdateId(userID, bson.M{
        "$set": bson.M{
            "todoPrefs":         todoPrefs,
            "notificationPrefs": notifPrefs,
            "updatedAt":         time.Now(),
        },
    })
}

func (r *MongoRepository) GetUserStats(userID string) (*users.UserStats, error) {
    // Mock implementation - in real app, this would aggregate data from task service
    return &users.UserStats{
        UserID:           userID,
        TotalTasks:       0,
        CompletedTasks:   0,
        PendingTasks:     0,
        OverdueTasks:     0,
        TotalProjects:    0,
        LastActivityDate: time.Now().Format("2006-01-02"),
    }, nil
}