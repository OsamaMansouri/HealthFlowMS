package com.healthflow.fhirnew.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.healthflow.fhirnew.entity.*;
import com.healthflow.fhirnew.repository.*;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api/fhir/proxy")
@Tag(name = "FHIR Proxy", description = "API for managing FHIR resources in local database")
public class FhirProxyController {

    @Autowired
    private FhirPatientRepository patientRepository;

    @Autowired
    private FhirEncounterRepository encounterRepository;

    @Autowired
    private FhirObservationRepository observationRepository;

    @Autowired
    private FhirConditionRepository conditionRepository;

    private final ObjectMapper objectMapper = new ObjectMapper();

    @GetMapping("/{resourceType}")
    @Operation(summary = "Get FHIR resources", description = "Retrieve FHIR resources by type and optionally by ID")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Successfully retrieved resource(s)"),
            @ApiResponse(responseCode = "500", description = "Error retrieving resources")
    })
    public ResponseEntity<?> getResources(
            @Parameter(description = "FHIR resource type (e.g., Patient, Encounter, Observation)") @PathVariable String resourceType,
            @Parameter(description = "Optional resource ID") @RequestParam(required = false) String id) {

        try {
            switch (resourceType) {
                case "Patient":
                    if (id != null) {
                        Optional<FhirPatient> patient = patientRepository.findByFhirId(id);
                        if (patient.isPresent()) {
                            return ResponseEntity.ok(patient.get().getResourceData());
                        }
                        return ResponseEntity.notFound().build();
                    } else {
                        List<FhirPatient> patients = patientRepository.findByActiveTrueOrderByCreatedAtDesc();
                        List<String> resources = new ArrayList<>();
                        for (FhirPatient p : patients) {
                            resources.add(p.getResourceData());
                        }
                        return ResponseEntity.ok(resources);
                    }

                case "Encounter":
                    if (id != null) {
                        Optional<FhirEncounter> encounter = encounterRepository.findByFhirId(id);
                        if (encounter.isPresent()) {
                            return ResponseEntity.ok(encounter.get().getResourceData());
                        }
                        return ResponseEntity.notFound().build();
                    }
                    return ResponseEntity.ok(encounterRepository.findAll());

                case "Observation":
                    if (id != null) {
                        Optional<FhirObservation> obs = observationRepository.findByFhirId(id);
                        if (obs.isPresent()) {
                            return ResponseEntity.ok(obs.get().getResourceData());
                        }
                        return ResponseEntity.notFound().build();
                    }
                    return ResponseEntity.ok(observationRepository.findAll());

                case "Condition":
                    if (id != null) {
                        Optional<FhirCondition> condition = conditionRepository.findByFhirId(id);
                        if (condition.isPresent()) {
                            return ResponseEntity.ok(condition.get().getResourceData());
                        }
                        return ResponseEntity.notFound().build();
                    }
                    return ResponseEntity.ok(conditionRepository.findAll());

                default:
                    return ResponseEntity.badRequest().body("Unsupported resource type: " + resourceType);
            }
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
            @Parameter(description = "FHIR resource type") @PathVariable String resourceType,
            @Parameter(description = "FHIR resource object") @RequestBody Map<String, Object> resource) {

        try {
            String jsonResource = objectMapper.writeValueAsString(resource);
            String resourceId = UUID.randomUUID().toString();

            // Add ID to the resource if not present
            if (!resource.containsKey("id")) {
                resource.put("id", resourceId);
            } else {
                resourceId = resource.get("id").toString();
            }

            switch (resourceType) {
                case "Patient":
                    FhirPatient patient = FhirPatient.builder()
                            .fhirId(resourceId)
                            .resourceData(objectMapper.writeValueAsString(resource))
                            .build();

                    // Extract fields for database
                    if (resource.containsKey("gender")) {
                        patient.setGender(resource.get("gender").toString());
                    }
                    if (resource.containsKey("birthDate")) {
                        patient.setBirthDate(resource.get("birthDate").toString());
                    }
                    patient.setActive(true);

                    FhirPatient savedPatient = patientRepository.save(patient);
                    resource.put("id", savedPatient.getFhirId());
                    return ResponseEntity.status(HttpStatus.CREATED).body(resource);

                case "Encounter":
                    FhirEncounter encounter = FhirEncounter.builder()
                            .fhirId(resourceId)
                            .resourceData(objectMapper.writeValueAsString(resource))
                            .build();
                    FhirEncounter savedEncounter = encounterRepository.save(encounter);
                    resource.put("id", savedEncounter.getFhirId());
                    return ResponseEntity.status(HttpStatus.CREATED).body(resource);

                case "Observation":
                    FhirObservation observation = FhirObservation.builder()
                            .fhirId(resourceId)
                            .resourceData(objectMapper.writeValueAsString(resource))
                            .build();
                    FhirObservation savedObs = observationRepository.save(observation);
                    resource.put("id", savedObs.getFhirId());
                    return ResponseEntity.status(HttpStatus.CREATED).body(resource);

                case "Condition":
                    FhirCondition condition = FhirCondition.builder()
                            .fhirId(resourceId)
                            .resourceData(objectMapper.writeValueAsString(resource))
                            .build();
                    FhirCondition savedCondition = conditionRepository.save(condition);
                    resource.put("id", savedCondition.getFhirId());
                    return ResponseEntity.status(HttpStatus.CREATED).body(resource);

                default:
                    return ResponseEntity.badRequest().body("Unsupported resource type: " + resourceType);
            }
        } catch (Exception e) {
            e.printStackTrace();
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
            @Parameter(description = "FHIR resource type") @PathVariable String resourceType,
            @Parameter(description = "Resource ID") @PathVariable String id,
            @Parameter(description = "Updated FHIR resource object") @RequestBody Map<String, Object> resource) {

        try {
            resource.put("id", id);
            String jsonResource = objectMapper.writeValueAsString(resource);

            switch (resourceType) {
                case "Patient":
                    Optional<FhirPatient> patientOpt = patientRepository.findByFhirId(id);
                    if (patientOpt.isPresent()) {
                        FhirPatient patient = patientOpt.get();
                        patient.setResourceData(jsonResource);
                        if (resource.containsKey("gender")) {
                            patient.setGender(resource.get("gender").toString());
                        }
                        if (resource.containsKey("birthDate")) {
                            patient.setBirthDate(resource.get("birthDate").toString());
                        }
                        patientRepository.save(patient);
                        return ResponseEntity.ok(resource);
                    }
                    return ResponseEntity.notFound().build();

                case "Encounter":
                    Optional<FhirEncounter> encounterOpt = encounterRepository.findByFhirId(id);
                    if (encounterOpt.isPresent()) {
                        FhirEncounter encounter = encounterOpt.get();
                        encounter.setResourceData(jsonResource);
                        encounterRepository.save(encounter);
                        return ResponseEntity.ok(resource);
                    }
                    return ResponseEntity.notFound().build();

                default:
                    return ResponseEntity.badRequest().body("Update not supported for: " + resourceType);
            }
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
            @Parameter(description = "FHIR resource type") @PathVariable String resourceType,
            @Parameter(description = "Resource ID") @PathVariable String id) {

        try {
            switch (resourceType) {
                case "Patient":
                    Optional<FhirPatient> patient = patientRepository.findByFhirId(id);
                    if (patient.isPresent()) {
                        patientRepository.delete(patient.get());
                        return ResponseEntity.noContent().build();
                    }
                    return ResponseEntity.notFound().build();

                case "Encounter":
                    Optional<FhirEncounter> encounter = encounterRepository.findByFhirId(id);
                    if (encounter.isPresent()) {
                        encounterRepository.delete(encounter.get());
                        return ResponseEntity.noContent().build();
                    }
                    return ResponseEntity.notFound().build();

                default:
                    return ResponseEntity.badRequest().body("Delete not supported for: " + resourceType);
            }
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Error: " + e.getMessage());
        }
    }
}
