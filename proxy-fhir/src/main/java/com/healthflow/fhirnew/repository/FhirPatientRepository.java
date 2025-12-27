package com.healthflow.fhirnew.repository;

import com.healthflow.fhirnew.entity.FhirPatient;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface FhirPatientRepository extends JpaRepository<FhirPatient, UUID> {
    Optional<FhirPatient> findByFhirId(String fhirId);

    List<FhirPatient> findByActiveTrueOrderByCreatedAtDesc();
}
