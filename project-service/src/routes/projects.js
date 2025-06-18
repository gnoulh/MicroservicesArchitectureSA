const express = require('express');
const router = express.Router();
const Project = require('../models/Project');

// GET /projects - List all projects (optionally filtered by user)
router.get('/', async (req, res) => {
  try {
    const { userId } = req.query;
    const projects = await Project.getAll(userId);
    res.json(projects);
  } catch (error) {
    console.error('Error fetching projects:', error);
    res.status(500).json({ error: 'Failed to fetch projects' });
  }
});

// POST /projects - Create new project
router.post('/', async (req, res) => {
  try {
    const { name, description, owner_id } = req.body;

    if (!name || !owner_id) {
      return res.status(400).json({ error: 'Name and owner_id are required' });
    }

    const project = await Project.create({ name, description, owner_id });
    res.status(201).json(project);
  } catch (error) {
    console.error('Error creating project:', error);
    res.status(500).json({ error: 'Failed to create project' });
  }
});

// GET /projects/:id - Get specific project
router.get('/:id', async (req, res) => {
  try {
    const project = await Project.getById(req.params.id);
    
    if (!project) {
      return res.status(404).json({ error: 'Project not found' });
    }

    // Get project members
    const members = await Project.getMembers(project.id);
    project.members = members;

    res.json(project);
  } catch (error) {
    console.error('Error fetching project:', error);
    res.status(500).json({ error: 'Failed to fetch project' });
  }
});

// PUT /projects/:id - Update project
router.put('/:id', async (req, res) => {
  try {
    const { name, description } = req.body;

    if (!name) {
      return res.status(400).json({ error: 'Name is required' });
    }

    const project = await Project.update(req.params.id, { name, description });
    
    if (!project) {
      return res.status(404).json({ error: 'Project not found' });
    }

    res.json(project);
  } catch (error) {
    console.error('Error updating project:', error);
    res.status(500).json({ error: 'Failed to update project' });
  }
});

// DELETE /projects/:id - Delete project
router.delete('/:id', async (req, res) => {
  try {
    const deleted = await Project.delete(req.params.id);
    
    if (!deleted) {
      return res.status(404).json({ error: 'Project not found' });
    }

    res.status(204).send();
  } catch (error) {
    console.error('Error deleting project:', error);
    res.status(500).json({ error: 'Failed to delete project' });
  }
});

// POST /projects/:id/members - Add member to project
router.post('/:id/members', async (req, res) => {
  try {
    const { user_id, role = 'MEMBER' } = req.body;

    if (!user_id) {
      return res.status(400).json({ error: 'user_id is required' });
    }

    await Project.addMember(req.params.id, user_id, role);
    const members = await Project.getMembers(req.params.id);
    
    res.status(201).json(members);
  } catch (error) {
    console.error('Error adding member:', error);
    res.status(500).json({ error: 'Failed to add member' });
  }
});

// GET /projects/user/:userId - Get user's projects
router.get('/user/:userId', async (req, res) => {
  try {
    const projects = await Project.getUserProjects(req.params.userId);
    res.json(projects);
  } catch (error) {
    console.error('Error fetching user projects:', error);
    res.status(500).json({ error: 'Failed to fetch user projects' });
  }
});

module.exports = router;