const { getSession } = require('../config/database');
const Task = require('../models/Task');

class CollaborationService {
  async shareTask(taskId, userId, permission = 'view') {
    const session = getSession();
    try {
      const result = await session.run(`
        MATCH (t:Task {id: $taskId})
        MATCH (u:User {id: $userId})
        MERGE (u)-[s:SHARED_WITH {permission: $permission, sharedAt: datetime()}]->(t)
        RETURN t, u, s
      `, { taskId, userId, permission });

      return result.records.length > 0;
    } finally {
      await session.close();
    }
  }

  async getSharedTasks(userId) {
    const session = getSession();
    try {
      const result = await session.run(`
        MATCH (u:User {id: $userId})-[s:SHARED_WITH]->(t:Task)
        RETURN t, s.permission as permission, s.sharedAt as sharedAt
        ORDER BY s.sharedAt DESC
      `, { userId });

      return result.records.map(record => ({
        task: record.get('t').properties,
        permission: record.get('permission'),
        sharedAt: record.get('sharedAt')
      }));
    } finally {
      await session.close();
    }
  }

  async addTaskComment(taskId, userId, comment) {
    const session = getSession();
    try {
      const commentId = require('uuid').v4();
      const result = await session.run(`
        MATCH (t:Task {id: $taskId})
        MATCH (u:User {id: $userId})
        CREATE (c:Comment {
          id: $commentId,
          content: $comment,
          createdAt: datetime()
        })
        CREATE (u)-[:COMMENTED]->(c)
        CREATE (c)-[:ON_TASK]->(t)
        RETURN c, u
      `, { taskId, userId, comment, commentId });

      return result.records[0]?.get('c').properties;
    } finally {
      await session.close();
    }
  }

  async getTaskActivity(taskId) {
    const session = getSession();
    try {
      const result = await session.run(`
        MATCH (t:Task {id: $taskId})
        OPTIONAL MATCH (u:User)-[:COMMENTED]->(c:Comment)-[:ON_TASK]->(t)
        OPTIONAL MATCH (sharer:User)-[s:SHARED_WITH]->(t)
        RETURN 
          collect(DISTINCT {
            type: 'comment',
            user: u.name,
            content: c.content,
            timestamp: c.createdAt
          }) as comments,
          collect(DISTINCT {
            type: 'shared',
            user: sharer.name,
            permission: s.permission,
            timestamp: s.sharedAt
          }) as shares
      `, { taskId });

      const record = result.records[0];
      const activities = [
        ...record.get('comments'),
        ...record.get('shares')
      ].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

      return activities;
    } finally {
      await session.close();
    }
  }

  async createTaskDependency(taskId, dependsOnTaskId) {
    const session = getSession();
    try {
      const result = await session.run(`
        MATCH (t1:Task {id: $taskId})
        MATCH (t2:Task {id: $dependsOnTaskId})
        MERGE (t1)-[:DEPENDS_ON]->(t2)
        RETURN t1, t2
      `, { taskId, dependsOnTaskId });

      return result.records.length > 0;
    } finally {
      await session.close();
    }
  }
}

module.exports = new CollaborationService();