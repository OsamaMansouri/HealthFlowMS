"""SQLAlchemy models for DeID service."""
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class DeidPatient(Base):
    """De-identified patient mapping."""
    __tablename__ = "deid_patients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_fhir_id = Column(String(100), unique=True, nullable=False)
    pseudo_id = Column(String(100), unique=True, nullable=False)
    deid_data = Column(JSON, nullable=False)
    age_group = Column(String(20))
    gender = Column(String(20))
    deid_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class DeidAuditLog(Base):
    """Audit log for de-identification operations."""
    __tablename__ = "deid_audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    operation = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)
    original_id = Column(String(100))
    pseudo_id = Column(String(100))
    fields_modified = Column(JSON)
    performed_at = Column(DateTime(timezone=True), server_default=func.now())


class FhirPatient(Base):
    """FHIR Patient (read-only from this service)."""
    __tablename__ = "fhir_patients"

    id = Column(UUID(as_uuid=True), primary_key=True)
    fhir_id = Column(String(100), unique=True, nullable=False)
    bundle_id = Column(UUID(as_uuid=True))
    resource_data = Column(JSON, nullable=False)
    identifier = Column(String(100))
    birth_date = Column(DateTime)
    gender = Column(String(20))
    deceased = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))


class FhirEncounter(Base):
    """FHIR Encounter (read-only from this service)."""
    __tablename__ = "fhir_encounters"

    id = Column(UUID(as_uuid=True), primary_key=True)
    fhir_id = Column(String(100), unique=True, nullable=False)
    patient_fhir_id = Column(String(100), nullable=False)
    bundle_id = Column(UUID(as_uuid=True))
    resource_data = Column(JSON, nullable=False)
    encounter_class = Column(String(50))
    status = Column(String(50))
    period_start = Column(DateTime(timezone=True))
    period_end = Column(DateTime(timezone=True))
    discharge_disposition = Column(String(100))
    service_type = Column(String(100))
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))


