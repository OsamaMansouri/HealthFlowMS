package com.healthflow.fhirnew.repository;

import com.healthflow.fhirnew.entity.FhirBundle;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.UUID;

import java.util.Optional;

@Repository
public interface FhirBundleRepository extends JpaRepository<FhirBundle, UUID> {
    Optional<FhirBundle> findByFhirId(String fhirId);
}

