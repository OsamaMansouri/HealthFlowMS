package com.healthflow.fhirnew.controller;

import com.healthflow.fhirnew.service.FhirSyncService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;
import static org.hamcrest.Matchers.*;

/**
 * Integration tests for FhirSyncController using MockMvc
 * Tests sync endpoints (now no-ops)
 */
@WebMvcTest(FhirSyncController.class)
class FhirSyncControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private FhirSyncService fhirSyncService;

    @Test
    void shouldReturnSuccessWhenSyncingAllFhirData() throws Exception {
        mockMvc.perform(post("/api/fhir/sync"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("success"))
                .andExpect(jsonPath("$.message", containsString("already synchronized")));
    }

    @Test
    void shouldReturnSuccessWhenSyncingSpecificResourceType() throws Exception {
        mockMvc.perform(post("/api/fhir/sync/Patient"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("success"))
                .andExpect(jsonPath("$.message", containsString("Patient")))
                .andExpect(jsonPath("$.message", containsString("already synchronized")));
    }

    @Test
    void shouldReturnSuccessForEncounterSync() throws Exception {
        mockMvc.perform(post("/api/fhir/sync/Encounter"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("success"));
    }

    @Test
    void shouldReturnSuccessForObservationSync() throws Exception {
        mockMvc.perform(post("/api/fhir/sync/Observation"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("success"));
    }

    @Test
    void shouldReturnSuccessForConditionSync() throws Exception {
        mockMvc.perform(post("/api/fhir/sync/Condition"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("success"));
    }

    @Test
    void shouldGetSyncedPatientsSuccessfully() throws Exception {
        mockMvc.perform(get("/api/fhir/sync/patients"))
                .andExpect(status().isOk());
    }
}
