package com.healthflow.fhirnew;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class FhirNewApplication {

    public static void main(String[] args) {
        SpringApplication.run(FhirNewApplication.class, args);
    }
}
