package com.healthflow.fhirnew.controller;

import com.healthflow.fhirnew.config.FhirClientConfig;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

@RestController
@RequestMapping("/api/fhir/proxy")
@Tag(name = "FHIR Proxy", description = "API for proxying FHIR resources to HAPI FHIR server")
public class FhirProxyController {

    @Autowired
    private FhirClientConfig fhirClientConfig;

    @Autowired
    private RestTemplate restTemplate;

    @GetMapping("/{resourceType}")
    @Operation(summary = "Get FHIR resources", description = "Retrieve FHIR resources by type and optionally by ID")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Successfully retrieved resource(s)"),
            @ApiResponse(responseCode = "500", description = "Error retrieving resources")
    })
    public ResponseEntity<?> getResources(
            @Parameter(description = "FHIR resource type (e.g., Patient, Encounter, Observation)")
            @PathVariable String resourceType,
            @Parameter(description = "Optional resource ID")
            @RequestParam(required = false) String id) {
        
        String url = fhirClientConfig.getFhirServerUrl() + "/" + resourceType;
        if (id != null) {
            url += "/" + id;
        }

        HttpHeaders headers = new HttpHeaders();
        headers.set("Content-Type", "application/fhir+json");
        HttpEntity<String> entity = new HttpEntity<>(headers);

        try {
            ResponseEntity<String> response = restTemplate.exchange(
                    url, HttpMethod.GET, entity, String.class);
            return ResponseEntity.ok(response.getBody());
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Error: " + e.getMessage());
        }
    }

    @PostMapping("/{resourceType}")
    @Operation(summary = "Create FHIR resource", description = "Create a new FHIR resource")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "201", description = "Resource created successfully"),
            @ApiResponse(responseCode = "500", description = "Error creating resource")
    })
    public ResponseEntity<?> createResource(
            @Parameter(description = "FHIR resource type")
            @PathVariable String resourceType,
            @Parameter(description = "FHIR resource object")
            @RequestBody Object resource) {
        
        String url = fhirClientConfig.getFhirServerUrl() + "/" + resourceType;

        HttpHeaders headers = new HttpHeaders();
        headers.set("Content-Type", "application/fhir+json");
        HttpEntity<Object> entity = new HttpEntity<>(resource, headers);

        try {
            ResponseEntity<String> response = restTemplate.exchange(
                    url, HttpMethod.POST, entity, String.class);
            return ResponseEntity.status(201).body(response.getBody());
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Error: " + e.getMessage());
        }
    }

    @PutMapping("/{resourceType}/{id}")
    @Operation(summary = "Update FHIR resource", description = "Update an existing FHIR resource")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Resource updated successfully"),
            @ApiResponse(responseCode = "500", description = "Error updating resource")
    })
    public ResponseEntity<?> updateResource(
            @Parameter(description = "FHIR resource type")
            @PathVariable String resourceType,
            @Parameter(description = "Resource ID")
            @PathVariable String id,
            @Parameter(description = "Updated FHIR resource object")
            @RequestBody Object resource) {
        
        String url = fhirClientConfig.getFhirServerUrl() + "/" + resourceType + "/" + id;

        HttpHeaders headers = new HttpHeaders();
        headers.set("Content-Type", "application/fhir+json");
        HttpEntity<Object> entity = new HttpEntity<>(resource, headers);

        try {
            ResponseEntity<String> response = restTemplate.exchange(
                    url, HttpMethod.PUT, entity, String.class);
            return ResponseEntity.ok(response.getBody());
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Error: " + e.getMessage());
        }
    }

    @DeleteMapping("/{resourceType}/{id}")
    @Operation(summary = "Delete FHIR resource", description = "Delete a FHIR resource by ID")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "204", description = "Resource deleted successfully"),
            @ApiResponse(responseCode = "500", description = "Error deleting resource")
    })
    public ResponseEntity<?> deleteResource(
            @Parameter(description = "FHIR resource type")
            @PathVariable String resourceType,
            @Parameter(description = "Resource ID")
            @PathVariable String id) {
        
        String url = fhirClientConfig.getFhirServerUrl() + "/" + resourceType + "/" + id;

        HttpHeaders headers = new HttpHeaders();
        HttpEntity<String> entity = new HttpEntity<>(headers);

        try {
            restTemplate.exchange(url, HttpMethod.DELETE, entity, String.class);
            return ResponseEntity.noContent().build();
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Error: " + e.getMessage());
        }
    }
}

