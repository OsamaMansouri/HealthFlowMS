package com.healthflow.fhirnew.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI fhirNewOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("FHIR New Service API")
                        .description("REST API for FHIR New Service - HealthFlowMS")
                        .version("1.0.0")
                        .contact(new Contact()
                                .name("HealthFlowMS Team")
                                .email("mansouri.osama@gmail.com"))
                        .license(new License()
                                .name("Apache 2.0")
                                .url("https://www.apache.org/licenses/LICENSE-2.0.html")))
                .servers(List.of(
                        new Server()
                                .url("http://localhost:8088")
                                .description("Local Development Server"),
                        new Server()
                                .url("http://healthflow-fhir-new:8088")
                                .description("Docker Container Server")
                ));
    }
}

