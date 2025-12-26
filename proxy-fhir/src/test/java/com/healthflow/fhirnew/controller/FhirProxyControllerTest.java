package com.healthflow.fhirnew.controller;

import com.healthflow.fhirnew.entity.FhirPatient;
import com.healthflow.fhirnew.repository.FhirConditionRepository;
import com.healthflow.fhirnew.repository.FhirEncounterRepository;
import com.healthflow.fhirnew.repository.FhirObservationRepository;
import com.healthflow.fhirnew.repository.FhirPatientRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.*;

import static org.hamcrest.Matchers.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * Integration tests for FhirProxyController using MockMvc
 * Tests REST endpoints directly
 */
@WebMvcTest(FhirProxyController.class)
class FhirProxyControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private FhirPatientRepository patientRepository;

    @MockBean
    private FhirEncounterRepository encounterRepository;

    @MockBean
    private FhirObservationRepository observationRepository;

    @MockBean
    private FhirConditionRepository conditionRepository;

    private FhirPatient testPatient;
    private String testPatientJson;

    @BeforeEach
    void setUp() {
        testPatient = new FhirPatient();
        testPatient.setId(UUID.randomUUID());
        testPatient.setFhirId("patient-123");
        testPatient.setGender("male");
        testPatient.setBirthDate("1990-01-01");
        testPatient.setActive(true);

        testPatientJson = """
                {
                    "resourceType": "Patient",
                    "id": "patient-123",
                    "gender": "male",
                    "birthDate": "1990-01-01",
                    "active": true
                }
                """;
    }

    // ==================== POST /Patient Tests ====================

    @Test
    void shouldCreatePatientSuccessfully() throws Exception {
        // Arrange
        when(patientRepository.findByFhirId("patient-123")).thenReturn(Optional.empty());
        when(patientRepository.save(any(FhirPatient.class))).thenReturn(testPatient);

        // Act & Assert
        mockMvc.perform(post("/api/fhir/proxy/Patient")
                .contentType(MediaType.APPLICATION_JSON)
                .content(testPatientJson))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value("patient-123"))
                .andExpect(jsonPath("$.resourceType").value("Patient"));

        verify(patientRepository, times(1)).save(any(FhirPatient.class));
    }

    @Test
    void shouldUpdateExistingPatient() throws Exception {
        // Arrange
        when(patientRepository.findByFhirId("patient-123")).thenReturn(Optional.of(testPatient));
        when(patientRepository.save(any(FhirPatient.class))).thenReturn(testPatient);

        // Act & Assert
        mockMvc.perform(post("/api/fhir/proxy/Patient")
                .contentType(MediaType.APPLICATION_JSON)
                .content(testPatientJson))
                .andExpect(status().isOk());

        verify(patientRepository, times(1)).findByFhirId("patient-123");
        verify(patientRepository, times(1)).save(any(FhirPatient.class));
    }

    @Test
    void shouldReturn400ForInvalidPatientJson() throws Exception {
        // Arrange
        String invalidJson = "{invalid json}";

        // Act & Assert
        mockMvc.perform(post("/api/fhir/proxy/Patient")
                .contentType(MediaType.APPLICATION_JSON)
                .content(invalidJson))
                .andExpect(status().is4xxClientError());
    }

    // ==================== GET /Patient Tests ====================

    @Test
    void shouldReturnAllActivePatients() throws Exception {
        // Arrange
        FhirPatient patient1 = createTestPatient("patient-1");
        FhirPatient patient2 = createTestPatient("patient-2");
        List<FhirPatient> patients = Arrays.asList(patient1, patient2);

        when(patientRepository.findByActiveTrueOrderByCreatedAtDesc()).thenReturn(patients);

        // Act & Assert
        mockMvc.perform(get("/api/fhir/proxy/Patient"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(2)))
                .andExpect(jsonPath("$[0].fhirId").value("patient-1"))
                .andExpect(jsonPath("$[1].fhirId").value("patient-2"));
    }

    @Test
    void shouldReturnEmptyListWhenNoPatientsExist() throws Exception {
        // Arrange
        when(patientRepository.findByActiveTrueOrderByCreatedAtDesc()).thenReturn(Collections.emptyList());

        // Act & Assert
        mockMvc.perform(get("/api/fhir/proxy/Patient"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(0)));
    }

    // ==================== GET /Patient/{id} Tests ====================

    @Test
    void shouldReturnPatientById() throws Exception {
        // Arrange
        when(patientRepository.findByFhirId("patient-123")).thenReturn(Optional.of(testPatient));

        // Act & Assert
        mockMvc.perform(get("/api/fhir/proxy/Patient")
                .param("id", "patient-123"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value("patient-123"))
                .andExpect(jsonPath("$.gender").value("male"));
    }

    @Test
    void shouldReturn404WhenPatientNotFound() throws Exception {
        // Arrange
        when(patientRepository.findByFhirId("nonexistent")).thenReturn(Optional.empty());

        // Act & Assert
        mockMvc.perform(get("/api/fhir/proxy/Patient")
                .param("id", "nonexistent"))
                .andExpect(status().isNotFound());
    }

    // ==================== POST /Encounter Tests ====================

    @Test
    void shouldCreateEncounterSuccessfully() throws Exception {
        // Arrange
        String encounterJson = """
                {
                    "resourceType": "Encounter",
                    "id": "encounter-123",
                    "subject": {"reference": "Patient/patient-123"},
                    "status": "finished"
                }
                """;

        // Act & Assert
        mockMvc.perform(post("/api/fhir/proxy/Encounter")
                .contentType(MediaType.APPLICATION_JSON)
                .content(encounterJson))
                .andExpect(status().isOk());

        verify(encounterRepository, times(1)).save(any());
    }

    // ==================== POST /Observation Tests ====================

    @Test
    void shouldCreateObservationSuccessfully() throws Exception {
        // Arrange
        String observationJson = """
                {
                    "resourceType": "Observation",
                    "id": "obs-123",
                    "subject": {"reference": "Patient/patient-123"},
                    "code": {"coding": [{"code": "8867-4"}]},
                    "valueQuantity": {"value": 72}
                }
                """;

        // Act & Assert
        mockMvc.perform(post("/api/fhir/proxy/Observation")
                .contentType(MediaType.APPLICATION_JSON)
                .content(observationJson))
                .andExpect(status().isOk());

        verify(observationRepository, times(1)).save(any());
    }

    // ==================== POST /Condition Tests ====================

    @Test
    void shouldCreateConditionSuccessfully() throws Exception {
        // Arrange
        String conditionJson = """
                {
                    "resourceType": "Condition",
                    "id": "condition-123",
                    "subject": {"reference": "Patient/patient-123"},
                    "code": {"coding": [{"code": "E11"}]}
                }
                """;

        // Act & Assert
        mockMvc.perform(post("/api/fhir/proxy/Condition")
                .contentType(MediaType.APPLICATION_JSON)
                .content(conditionJson))
                .andExpect(status().isOk());

        verify(conditionRepository, times(1)).save(any());
    }

    // ==================== PUT /Patient/{id} Tests ====================

    @Test
    void shouldUpdatePatientByIdSuccessfully() throws Exception {
        // Arrange
        when(patientRepository.findByFhirId("patient-123")).thenReturn(Optional.of(testPatient));
        when(patientRepository.save(any(FhirPatient.class))).thenReturn(testPatient);

        String updatedJson = """
                {
                    "resourceType": "Patient",
                    "id": "patient-123",
                    "gender": "female",
                    "birthDate": "1990-01-01",
                    "active": true
                }
                """;

        // Act & Assert
        mockMvc.perform(put("/api/fhir/proxy/Patient/patient-123")
                .contentType(MediaType.APPLICATION_JSON)
                .content(updatedJson))
                .andExpect(status().isOk());

        verify(patientRepository, times(1)).save(any(FhirPatient.class));
    }

    // ==================== DELETE /Patient/{id} Tests ====================

    @Test
    void shouldDeletePatientByIdSuccessfully() throws Exception {
        // Arrange
        when(patientRepository.findByFhirId("patient-123")).thenReturn(Optional.of(testPatient));

        // Act & Assert
        mockMvc.perform(delete("/api/fhir/proxy/Patient/patient-123"))
                .andExpect(status().isOk());

        verify(patientRepository, times(1)).delete(any(FhirPatient.class));
    }

    @Test
    void shouldReturn404WhenDeletingNonexistentPatient() throws Exception {
        // Arrange
        when(patientRepository.findByFhirId("nonexistent")).thenReturn(Optional.empty());

        // Act & Assert
        mockMvc.perform(delete("/api/fhir/proxy/Patient/nonexistent"))
                .andExpect(status().isNotFound());
    }

    // ==================== Edge Cases ====================

    @Test
    void shouldHandleNullRequestBody() throws Exception {
        mockMvc.perform(post("/api/fhir/proxy/Patient")
                .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().is4xxClientError());
    }

    @Test
    void shouldHandleEmptyRequestBody() throws Exception {
        mockMvc.perform(post("/api/fhir/proxy/Patient")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{}"))
                .andExpect(status().is4xxClientError());
    }

    // ==================== Helper Methods ====================

    private FhirPatient createTestPatient(String fhirId) {
        FhirPatient patient = new FhirPatient();
        patient.setId(UUID.randomUUID());
        patient.setFhirId(fhirId);
        patient.setGender("male");
        patient.setBirthDate("1990-01-01");
        patient.setActive(true);
        return patient;
    }
}
