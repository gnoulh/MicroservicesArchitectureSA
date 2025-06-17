const db = require('../config/database');
const { v4: uuidv4 } = require('uuid');

class Project {
  static async getAll(userId = null) {
    let query = `
      SELECT DISTINCT p.*, pm.role 
      FROM projects p 
      LEFT JOIN project_members pm ON p.id = pm.project_id
    `;
    let params = [];

    if (userId) {
      query += ' WHERE pm.user_id = ? OR p.owner_id = ?';
      params = [userId, userId];
    }

    query += ' ORDER BY p.created_at DESC';

    const [rows] = await db.execute(query, params);
    return rows;
  }

  static async getById(id) {
    const [rows] = await db.execute(
      'SELECT * FROM projects WHERE id = ?',
      [id]
    );
    return rows[0];
  }

  static async create(projectData) {
    const id = uuidv4();
    const { name, description, owner_id } = projectData;

    await db.execute(
      'INSERT INTO projects (id, name, description, owner_id) VALUES (?, ?, ?, ?)',
      [id, name, description, owner_id]
    );

    // Add owner as project member
    await db.execute(
      'INSERT INTO project_members (project_id, user_id, role) VALUES (?, ?, ?)',
      [id, owner_id, 'OWNER']
    );

    return this.getById(id);
  }

  static async update(id, projectData) {
    const { name, description } = projectData;
    
    await db.execute(
      'UPDATE projects SET name = ?, description = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
      [name, description, id]
    );

    return this.getById(id);
  }

  static async delete(id) {
    const [result] = await db.execute('DELETE FROM projects WHERE id = ?', [id]);
    return result.affectedRows > 0;
  }

  static async getMembers(projectId) {
    const [rows] = await db.execute(
      'SELECT user_id, role, joined_at FROM project_members WHERE project_id = ?',
      [projectId]
    );
    return rows;
  }

  static async addMember(projectId, userId, role = 'MEMBER') {
    await db.execute(
      'INSERT INTO project_members (project_id, user_id, role) VALUES (?, ?, ?) ON DUPLICATE KEY UPDATE role = VALUES(role)',
      [projectId, userId, role]
    );
    return true;
  }

  static async removeMember(projectId, userId) {
    const [result] = await db.execute(
      'DELETE FROM project_members WHERE project_id = ? AND user_id = ?',
      [projectId, userId]
    );
    return result.affectedRows > 0;
  }

  static async getUserProjects(userId) {
    const [rows] = await db.execute(`
      SELECT p.*, pm.role 
      FROM projects p 
      JOIN project_members pm ON p.id = pm.project_id 
      WHERE pm.user_id = ? 
      ORDER BY p.created_at DESC
    `, [userId]);
    return rows;
  }
}

module.exports = Project;