CREATE DATABASE IF NOT EXISTS todo_projects;
USE todo_projects;

CREATE TABLE projects (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_owner_id (owner_id)
);

CREATE TABLE project_members (
    project_id VARCHAR(36),
    user_id VARCHAR(36),
    role VARCHAR(50) DEFAULT 'MEMBER',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (project_id, user_id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
);

-- Insert sample data
INSERT INTO projects (id, name, description, owner_id) VALUES 
('550e8400-e29b-41d4-a716-446655440001', 'Personal Tasks', 'My personal todo items', 'user123'),
('550e8400-e29b-41d4-a716-446655440002', 'Work Project', 'Team collaboration project', 'user123');

INSERT INTO project_members (project_id, user_id, role) VALUES 
('550e8400-e29b-41d4-a716-446655440001', 'user123', 'OWNER'),
('550e8400-e29b-41d4-a716-446655440002', 'user123', 'OWNER'),
('550e8400-e29b-41d4-a716-446655440002', 'user456', 'MEMBER');