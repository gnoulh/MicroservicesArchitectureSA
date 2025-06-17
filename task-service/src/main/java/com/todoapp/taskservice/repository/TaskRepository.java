package com.todoapp.taskservice.repository;

import com.todoapp.taskservice.model.Task;
import com.todoapp.taskservice.model.TaskStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface TaskRepository extends JpaRepository<Task, UUID> {
    
    List<Task> findByAssignedUserId(UUID assignedUserId);
    
    List<Task> findByProjectId(UUID projectId);
    
    List<Task> findByStatus(TaskStatus status);
    
    @Query("SELECT t FROM Task t WHERE t.assignedUserId = :userId AND t.status = :status")
    List<Task> findByAssignedUserIdAndStatus(@Param("userId") UUID userId, @Param("status") TaskStatus status);
    
    @Query("SELECT t FROM Task t WHERE t.projectId = :projectId AND t.status = :status")
    List<Task> findByProjectIdAndStatus(@Param("projectId") UUID projectId, @Param("status") TaskStatus status);
    
    long countByAssignedUserId(UUID assignedUserId);
    
    long countByProjectId(UUID projectId);
}
