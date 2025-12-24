package com.healthflow.fhirnew.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/test")
@Tag(name = "Test", description = "Test connection endpoint for frontend")
public class TestController {

    @PostMapping
    @Operation(summary = "Test connection endpoint", description = "Endpoint for frontend to test connection to proxy-fhir service.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Connection test successful")
    })
    public ResponseEntity<Map<String, Object>> testConnection(@RequestBody(required = false) Map<String, Object> body) {
        Map<String, Object> response = new HashMap<>();
        response.put("status", "OK");
        response.put("message", "Connection test successful");
        response.put("service", "fhir-new");
        response.put("timestamp", LocalDateTime.now());
        return ResponseEntity.ok(response);
    }

    @GetMapping
    @Operation(summary = "Test connection endpoint (GET)", description = "Endpoint for frontend to test connection to proxy-fhir service.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Connection test successful")
    })
    public ResponseEntity<Map<String, Object>> testConnectionGet() {
        Map<String, Object> response = new HashMap<>();
        response.put("status", "OK");
        response.put("message", "Connection test successful");
        response.put("service", "fhir-new");
        response.put("timestamp", LocalDateTime.now());
        return ResponseEntity.ok(response);
    }
}

