package com.healthflow.fhirnew.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

@Service
public class FhirScheduledSyncService {

    private static final Logger logger = LoggerFactory.getLogger(FhirScheduledSyncService.class);

    @Autowired
    private FhirSyncService fhirSyncService;

    /**
     * Scheduled task to synchronize FHIR resources from HAPI FHIR server
     * Runs every 15 minutes as configured in application.yml
     */
    @Scheduled(cron = "${fhir.sync.cron:0 */15 * * * *}")
    public void scheduledSync() {
        logger.info("Starting scheduled FHIR synchronization...");

        try {
            fhirSyncService.syncAllResources();
            logger.info("Scheduled FHIR synchronization completed successfully");
        } catch (Exception e) {
            logger.error("Error during scheduled FHIR synchronization: {}", e.getMessage(), e);
        }
    }
}
