package com.todoapp.taskservice.health;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.sql.DataSource;
import java.sql.Connection;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestController
public class HealthController {

    @Autowired
    private DataSource dataSource;

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        return readiness();
    }

    @GetMapping("/health/live")
    public ResponseEntity<Map<String, Object>> liveness() {
        Map<String, Object> response = new HashMap<>();
        response.put("status", "UP");
        response.put("timestamp", LocalDateTime.now());
        response.put("checks", new HashMap<String, String>());
        
        return ResponseEntity.ok(response);
    }

    @GetMapping("/health/ready")
    public ResponseEntity<Map<String, Object>> readiness() {
        Map<String, Object> response = new HashMap<>();
        Map<String, String> checks = new HashMap<>();
        
        response.put("timestamp", LocalDateTime.now());
        
        // Check database connectivity
        try (Connection connection = dataSource.getConnection()) {
            if (connection.isValid(5)) {
                checks.put("database", "OK");
                response.put("status", "UP");
            } else {
                checks.put("database", "FAIL: Invalid connection");
                response.put("status", "DOWN");
            }
        } catch (Exception e) {
            checks.put("database", "FAIL: " + e.getMessage());
            response.put("status", "DOWN");
        }
        
        response.put("checks", checks);
        
        if ("DOWN".equals(response.get("status"))) {
            return ResponseEntity.status(503).body(response);
        }
        
        return ResponseEntity.ok(response);
    }
}