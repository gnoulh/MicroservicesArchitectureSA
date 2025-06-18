package com.todoapp.taskservice.service;

import com.todoapp.taskservice.dto.TaskCreateRequest;
import com.todoapp.taskservice.dto.TaskUpdateRequest;
import com.todoapp.taskservice.model.Task;
import com.todoapp.taskservice.model.TaskStatus;
import com.todoapp.taskservice.repository.TaskRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;

@Service
public class TaskService {
    
    @Autowired
    private TaskRepository taskRepository;
    
    public List<Task> getAllTasks() {
        return taskRepository.findAll();
    }
    
    public Task getTaskById(UUID id) {
        return taskRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Task not found with id: " + id));
    }
    
    public Task createTask(TaskCreateRequest request) {
        Task task = new Task();
        task.setTitle(request.getTitle());
        task.setDescription(request.getDescription());
        
        if (request.getStatus() != null) {
            task.setStatus(request.getStatus());
        }
        if (request.getPriority() != null) {
            task.setPriority(request.getPriority());
        }
        
        task.setDueDate(request.getDueDate());
        task.setProjectId(request.getProjectId());
        task.setAssignedUserId(request.getAssignedUserId());
        
        return taskRepository.save(task);
    }
    
    public Task updateTask(UUID id, TaskUpdateRequest request) {
        Task task = getTaskById(id);
        
        if (request.getTitle() != null) {
            task.setTitle(request.getTitle());
        }
        if (request.getDescription() != null) {
            task.setDescription(request.getDescription());
        }
        if (request.getStatus() != null) {
            task.setStatus(request.getStatus());
        }
        if (request.getPriority() != null) {
            task.setPriority(request.getPriority());
        }
        if (request.getDueDate() != null) {
            task.setDueDate(request.getDueDate());
        }
        if (request.getProjectId() != null) {
            task.setProjectId(request.getProjectId());
        }
        if (request.getAssignedUserId() != null) {
            task.setAssignedUserId(request.getAssignedUserId());
        }
        
        return taskRepository.save(task);
    }
    
    public void deleteTask(UUID id) {
        Task task = getTaskById(id);
        taskRepository.delete(task);
    }
    
    public List<Task> getTasksByUserId(UUID userId) {
        return taskRepository.findByAssignedUserId(userId);
    }
    
    public List<Task> getTasksByProjectId(UUID projectId) {
        return taskRepository.findByProjectId(projectId);
    }
    
    public List<Task> getTasksByStatus(TaskStatus status) {
        return taskRepository.findByStatus(status);
    }
    
    public List<Task> getTasksByUserIdAndStatus(UUID userId, TaskStatus status) {
        return taskRepository.findByAssignedUserIdAndStatus(userId, status);
    }
}
