package com.healthflow.fhirnew.repository;

import com.healthflow.fhirnew.entity.FhirCondition;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface FhirConditionRepository extends JpaRepository<FhirCondition, UUID> {
    Optional<FhirCondition> findByFhirId(String fhirId);
}
