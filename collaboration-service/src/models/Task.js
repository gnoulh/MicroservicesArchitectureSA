const { v4: uuidv4 } = require('uuid');

class Task {
  constructor(data) {
    this.id = data.id || uuidv4();
    this.title = data.title;
    this.description = data.description;
    this.status = data.status || 'TODO';
    this.priority = data.priority || 'MEDIUM';
    this.projectId = data.projectId;
    this.assignedUserId = data.assignedUserId;
    this.createdAt = data.createdAt || new Date().toISOString();
    this.updatedAt = data.updatedAt || new Date().toISOString();
  }

  toNeo4jProperties() {
    return {
      id: this.id,
      title: this.title,
      description: this.description,
      status: this.status,
      priority: this.priority,
      projectId: this.projectId,
      assignedUserId: this.assignedUserId,
      createdAt: this.createdAt,
      updatedAt: this.updatedAt
    };
  }
}

module.exports = Task;