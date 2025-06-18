const express = require('express');
const router = express.Router();
const CollaborationController = require('../controllers/CollaborationController');

// Share a task with another user
router.post('/tasks/:id/share', CollaborationController.shareTask);

// Get all tasks shared with a user
router.get('/user/:userId/shared-tasks', CollaborationController.getSharedTasks);

// Add comment to a task
router.post('/tasks/:id/comments', CollaborationController.addComment);

// Get task activity feed
router.get('/tasks/:id/activity', CollaborationController.getTaskActivity);

module.exports = router;