package com.healthflow.fhirnew.repository;

import com.healthflow.fhirnew.entity.FhirObservation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.UUID;

import java.util.List;
import java.util.Optional;

@Repository
public interface FhirObservationRepository extends JpaRepository<FhirObservation, UUID> {
    Optional<FhirObservation> findByFhirId(String fhirId);
    List<FhirObservation> findByPatientFhirId(String patientFhirId);
}

