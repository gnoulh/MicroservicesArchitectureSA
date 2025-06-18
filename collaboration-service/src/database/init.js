const { getSession } = require('../config/database');

async function createConstraints() {
  const session = getSession();
  try {
    // Create constraints and indexes
    await session.run('CREATE CONSTRAINT task_id IF NOT EXISTS FOR (t:Task) REQUIRE t.id IS UNIQUE');
    await session.run('CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE');
    await session.run('CREATE CONSTRAINT comment_id IF NOT EXISTS FOR (c:Comment) REQUIRE c.id IS UNIQUE');
    
    console.log('Database constraints created successfully');
  } catch (error) {
    console.error('Error creating constraints:', error);
  } finally {
    await session.close();
  }
}

async function seedData() {
  const session = getSession();
  try {
    // Create sample users
    await session.run(`
      MERGE (u1:User {id: '123', name: 'John Doe', email: 'john@example.com'})
      MERGE (u2:User {id: '456', name: 'Jane Smith', email: 'jane@example.com'})
    `);

    // Create sample tasks
    await session.run(`
      MERGE (t1:Task {
        id: 'task-1',
        title: 'Sample Task 1',
        description: 'This is a sample task',
        status: 'TODO',
        priority: 'HIGH',
        projectId: 'project-1',
        assignedUserId: '123',
        createdAt: datetime(),
        updatedAt: datetime()
      })
      MERGE (t2:Task {
        id: 'task-2',
        title: 'Sample Task 2',
        description: 'Another sample task',
        status: 'IN_PROGRESS',
        priority: 'MEDIUM',
        projectId: 'project-1',
        assignedUserId: '456',
        createdAt: datetime(),
        updatedAt: datetime()
      })
    `);

    console.log('Sample data seeded successfully');
  } catch (error) {
    console.error('Error seeding data:', error);
  } finally {
    await session.close();
  }
}

module.exports = { createConstraints, seedData };