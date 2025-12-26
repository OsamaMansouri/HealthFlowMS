package com.healthflow.fhirnew.controller;

import com.healthflow.fhirnew.service.FhirSyncService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/fhir/sync")
@Tag(name = "FHIR Sync", description = "API for synchronizing FHIR data from HAPI FHIR server to PostgreSQL")
public class FhirSyncController {

    @Autowired
    private FhirSyncService fhirSyncService;

    @PostMapping
    @Operation(summary = "Sync all FHIR resources", description = "Synchronize all FHIR resources from HAPI FHIR server to PostgreSQL")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Synchronization completed successfully"),
            @ApiResponse(responseCode = "500", description = "Error during synchronization")
    })
    public ResponseEntity<?> syncFhirData() {
        // Since we're now storing FHIR resources directly in the database,
        // no sync is needed. Return success immediately.
        return ResponseEntity.ok()
                .body("{\"status\": \"success\", \"message\": \"FHIR data already synchronized (stored directly)\"}");
    }

    @PostMapping("/{resourceType}")
    @Operation(summary = "Sync specific resource type", description = "Synchronize a specific FHIR resource type from HAPI FHIR server")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Resource type synchronized successfully"),
            @ApiResponse(responseCode = "500", description = "Error during synchronization")
    })
    public ResponseEntity<?> syncResourceType(
            @Parameter(description = "FHIR resource type (Patient, Encounter, Observation, etc.)") @PathVariable String resourceType) {
        // Since we're now storing FHIR resources directly in the database,
        // no sync is needed. Return success immediately.
        return ResponseEntity.ok()
                .body("{\"status\": \"success\", \"message\": \"" + resourceType
                        + " already synchronized (stored directly)\"}");
    }

    @GetMapping("/patients")
    @Operation(summary = "Get synchronized patients", description = "Retrieve list of all synchronized patients from PostgreSQL")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Successfully retrieved patients"),
            @ApiResponse(responseCode = "500", description = "Error retrieving patients")
    })
    public ResponseEntity<?> getSyncedPatients() {
        try {
            return ResponseEntity.ok(fhirSyncService.getAllPatients());
        } catch (Exception e) {
            return ResponseEntity.status(500).body("{\"status\": \"error\", \"message\": \"" + e.getMessage() + "\"}");
        }
    }
}
