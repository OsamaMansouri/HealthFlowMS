package com.healthflow.fhirnew.service;

import com.healthflow.fhirnew.config.FhirClientConfig;
import com.healthflow.fhirnew.entity.*;
import com.healthflow.fhirnew.repository.*;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class FhirSyncService {

    @Autowired
    private FhirClientConfig fhirClientConfig;

    @Autowired
    private RestTemplate restTemplate;

    @Autowired
    private FhirPatientRepository patientRepository;

    @Autowired
    private FhirEncounterRepository encounterRepository;

    @Autowired
    private FhirObservationRepository observationRepository;

    @Autowired
    private FhirBundleRepository bundleRepository;

    @Autowired
    private FhirConditionRepository conditionRepository;

    private final ObjectMapper objectMapper = new ObjectMapper();

    public void syncAllResources() {
        syncResourceType("Patient");
        syncResourceType("Encounter");
        syncResourceType("Observation");
        syncResourceType("Condition");
    }

    public Object getAllPatients() {
        return patientRepository.findAll();
    }

    public void syncResourceType(String resourceType) {
        try {
            String url = fhirClientConfig.getFhirServerUrl() + "/" + resourceType;
            String response = restTemplate.getForObject(url, String.class);

            if (response != null) {
                JsonNode bundle = objectMapper.readTree(response);
                JsonNode entries = bundle.get("entry");

                if (entries != null && entries.isArray()) {
                    for (JsonNode entry : entries) {
                        JsonNode resource = entry.get("resource");
                        if (resource != null) {
                            saveResource(resourceType, resource);
                        }
                    }
                }
            }
        } catch (Exception e) {
            throw new RuntimeException("Error syncing " + resourceType + ": " + e.getMessage(), e);
        }
    }

    private void saveResource(String resourceType, JsonNode resource) {
        String fhirId = resource.get("id").asText();
        String resourceData = resource.toString();

        switch (resourceType) {
            case "Patient":
                savePatient(fhirId, resourceData);
                break;
            case "Encounter":
                saveEncounter(fhirId, resourceData, resource);
                break;
            case "Observation":
                saveObservation(fhirId, resourceData, resource);
                break;
            case "Condition":
                saveCondition(fhirId, resourceData, resource);
                break;
            default:
                break;
        }
    }

    private void savePatient(String fhirId, String resourceData) {
        FhirPatient patient = patientRepository.findByFhirId(fhirId)
                .orElse(FhirPatient.builder().fhirId(fhirId).build());
        patient.setResourceData(resourceData);
        patientRepository.save(patient);
    }

    private void saveEncounter(String fhirId, String resourceData, JsonNode resource) {
        String patientFhirId = null;
        JsonNode subject = resource.get("subject");
        if (subject != null && subject.has("reference")) {
            String reference = subject.get("reference").asText();
            if (reference.startsWith("Patient/")) {
                patientFhirId = reference.substring(8);
            }
        }

        FhirEncounter encounter = encounterRepository.findByFhirId(fhirId)
                .orElse(FhirEncounter.builder().fhirId(fhirId).build());
        encounter.setResourceData(resourceData);
        encounter.setPatientFhirId(patientFhirId);
        encounterRepository.save(encounter);
    }

    private void saveObservation(String fhirId, String resourceData, JsonNode resource) {
        String patientFhirId = null;
        JsonNode subject = resource.get("subject");
        if (subject != null && subject.has("reference")) {
            String reference = subject.get("reference").asText();
            if (reference.startsWith("Patient/")) {
                patientFhirId = reference.substring(8);
            }
        }

        FhirObservation observation = observationRepository.findByFhirId(fhirId)
                .orElse(FhirObservation.builder().fhirId(fhirId).build());
        observation.setResourceData(resourceData);
        observation.setPatientFhirId(patientFhirId);
        observationRepository.save(observation);
    }

    private void saveCondition(String fhirId, String resourceData, JsonNode resource) {
        String patientFhirId = null;
        JsonNode subject = resource.get("subject");
        if (subject != null && subject.has("reference")) {
            String reference = subject.get("reference").asText();
            if (reference.startsWith("Patient/")) {
                patientFhirId = reference.substring(8);
            }
        }

        FhirCondition condition = conditionRepository.findByFhirId(fhirId)
                .orElse(FhirCondition.builder().fhirId(fhirId).build());
        condition.setResourceData(resourceData);
        condition.setPatientFhirId(patientFhirId);
        conditionRepository.save(condition);
    }
}
