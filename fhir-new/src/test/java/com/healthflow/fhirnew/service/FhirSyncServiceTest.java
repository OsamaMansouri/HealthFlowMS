package com.healthflow.fhirnew.service;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

@SpringBootTest
@ActiveProfiles("test")
class FhirSyncServiceTest {

    @Autowired
    private FhirSyncService fhirSyncService;

    @Test
    void testSyncServiceExists() {
        // Basic test to ensure service is loaded
        assert fhirSyncService != null;
    }
}

