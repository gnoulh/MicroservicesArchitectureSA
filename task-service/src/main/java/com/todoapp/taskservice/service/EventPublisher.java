package com.todo.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.todo.config.RabbitMQConfig;
import com.todo.model.Task;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@Service
public class EventPublisher {
    
    @Autowired
    private RabbitTemplate rabbitTemplate;
    
    @Autowired
    private ObjectMapper objectMapper;
    
    public void publishTaskCreated(Task task) {
        Map<String, Object> event = createBaseEvent("task.created");
        Map<String, Object> data = new HashMap<>();
        data.put("taskId", task.getId());
        data.put("title", task.getTitle());
        data.put("description", task.getDescription());
        data.put("projectId", task.getProjectId());
        data.put("assignedUserId", task.getAssignedUserId());
        data.put("priority", task.getPriority());
        data.put("dueDate", task.getDueDate());
        data.put("createdBy", task.getCreatedBy());
        
        event.put("data", data);
        
        rabbitTemplate.convertAndSend(
            RabbitMQConfig.EXCHANGE_NAME,
            "task.created",
            event
        );
    }
    
    public void publishTaskUpdated(Task task, Map<String, Object> changes) {
        Map<String, Object> event = createBaseEvent("task.updated");
        Map<String, Object> data = new HashMap<>();
        data.put("taskId", task.getId());
        data.put("changes", changes);
        data.put("updatedBy", task.getUpdatedBy());
        
        event.put("data", data);
        
        rabbitTemplate.convertAndSend(
            RabbitMQConfig.EXCHANGE_NAME,
            "task.updated",
            event
        );
    }
    
    public void publishTaskCompleted(Task task) {
        Map<String, Object> event = createBaseEvent("task.completed");
        Map<String, Object> data = new HashMap<>();
        data.put("taskId", task.getId());
        data.put("completedBy", task.getCompletedBy());
        data.put("completionTime", Instant.now().toString());
        
        event.put("data", data);
        
        rabbitTemplate.convertAndSend(
            RabbitMQConfig.EXCHANGE_NAME,
            "task.completed",
            event
        );
    }
    
    private Map<String, Object> createBaseEvent(String eventType) {
        Map<String, Object> event = new HashMap<>();
        event.put("eventId", UUID.randomUUID().toString());
        event.put("timestamp", Instant.now().toString());
        event.put("eventType", eventType);
        event.put("version", "1.0");
        return event;
    }
}