-- Sample tasks for testing
INSERT INTO tasks (id, title, description, status, priority, assigned_user_id) VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'Setup Project Structure', 'Initialize the project with proper directory structure', 'COMPLETED', 'HIGH', '550e8400-e29b-41d4-a716-446655440101'),
    ('550e8400-e29b-41d4-a716-446655440002', 'Implement User Authentication', 'Add login and registration functionality', 'IN_PROGRESS', 'HIGH', '550e8400-e29b-41d4-a716-446655440101'),
    ('550e8400-e29b-41d4-a716-446655440003', 'Design Database Schema', 'Create tables for users, tasks, and projects', 'TODO', 'MEDIUM', '550e8400-e29b-41d4-a716-446655440102')
ON CONFLICT (id) DO NOTHING;