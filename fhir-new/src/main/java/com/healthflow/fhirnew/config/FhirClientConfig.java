package com.healthflow.fhirnew.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

@Configuration
public class FhirClientConfig {

    @Value("${fhir.server.url}")
    private String fhirServerUrl;

    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }

    public String getFhirServerUrl() {
        return fhirServerUrl;
    }
}

