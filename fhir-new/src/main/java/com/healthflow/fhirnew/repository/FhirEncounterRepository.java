package com.healthflow.fhirnew.repository;

import com.healthflow.fhirnew.entity.FhirEncounter;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.UUID;

import java.util.List;
import java.util.Optional;

@Repository
public interface FhirEncounterRepository extends JpaRepository<FhirEncounter, UUID> {
    Optional<FhirEncounter> findByFhirId(String fhirId);
    List<FhirEncounter> findByPatientFhirId(String patientFhirId);
}

