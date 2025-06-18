const CollaborationService = require('../services/CollaborationService');
const Joi = require('joi');

class CollaborationController {
  async shareTask(req, res) {
    try {
      const schema = Joi.object({
        userId: Joi.string().required(),
        permission: Joi.string().valid('view', 'edit').default('view')
      });

      const { error, value } = schema.validate(req.body);
      if (error) {
        return res.status(400).json({ error: error.details[0].message });
      }

      const { id: taskId } = req.params;
      const { userId, permission } = value;

      const result = await CollaborationService.shareTask(taskId, userId, permission);
      
      if (result) {
        res.json({ message: 'Task shared successfully' });
      } else {
        res.status(404).json({ error: 'Task or user not found' });
      }
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }

  async getSharedTasks(req, res) {
    try {
      const { userId } = req.params;
      const tasks = await CollaborationService.getSharedTasks(userId);
      res.json(tasks);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }

  async addComment(req, res) {
    try {
      const schema = Joi.object({
        userId: Joi.string().required(),
        comment: Joi.string().required()
      });

      const { error, value } = schema.validate(req.body);
      if (error) {
        return res.status(400).json({ error: error.details[0].message });
      }

      const { id: taskId } = req.params;
      const { userId, comment } = value;

      const result = await CollaborationService.addTaskComment(taskId, userId, comment);
      res.status(201).json(result);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }

  async getTaskActivity(req, res) {
    try {
      const { id: taskId } = req.params;
      const activity = await CollaborationService.getTaskActivity(taskId);
      res.json(activity);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }
}

module.exports = new CollaborationController();