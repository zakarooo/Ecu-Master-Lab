from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


# ==========================================================
# ENUMS
# ==========================================================

class ProjectStatus(str, enum.Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"


class UserRole(str, enum.Enum):
    CLIENT = "client"
    EXPERT = "expert"
    ADMIN = "admin"


class JobStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


# ==========================================================
# USER
# ==========================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)

    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(30))

    hashed_password = Column(String(255), nullable=False)

    role = Column(SQLEnum(UserRole), default=UserRole.CLIENT)

    is_active = Column(Boolean, default=True)
    is_email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String(255), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    projects = relationship("Project", back_populates="owner")


# ==========================================================
# PROJECT
# ==========================================================

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    status = Column(
        SQLEnum(ProjectStatus),
        default=ProjectStatus.PENDING,
    )

    vehicle_make = Column(String(100))
    vehicle_model = Column(String(100))
    vehicle_year = Column(Integer)
    vehicle_engine = Column(String(100))
    vehicle_power = Column(String(50))
    vehicle_ecu_type = Column(String(100))
    vehicle_mileage = Column(Integer)
    vehicle_gearbox = Column(String(50))
    vehicle_vin = Column(String(17))

    tool_used = Column(String(100))

    ecu_filename = Column(String(255))
    ecu_file_path = Column(String(500))
    ecu_file_size = Column(Integer)
    ecu_file_hash = Column(String(64))
    ecu_original_backup = Column(String(500))

    ai_detected_ecu = Column(String(100))
    ai_detected_hw = Column(String(100))
    ai_detected_sw = Column(String(100))
    ai_checksum_valid = Column(Boolean)
    ai_confidence = Column(Float)
    ai_analysis_json = Column(Text)

    modifications = Column(Text)

    rejection_reason = Column(Text)

    client_notes = Column(Text)

    result_file_path = Column(String(500))
    result_checksum = Column(String(64))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="projects")

    vehicle = relationship(
        "Vehicle",
        uselist=False,
        back_populates="project",
        cascade="all, delete-orphan",
    )

    ecu = relationship(
        "ECU",
        uselist=False,
        back_populates="project",
        cascade="all, delete-orphan",
    )

    jobs = relationship(
        "Job",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    file_versions = relationship(
        "FileVersion",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    ecu_files = relationship(
        "ECUFile",
        back_populates="project",
        foreign_keys="ECUFile.project_id",
    )


# ==========================================================
# VEHICLE
# ==========================================================

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        unique=True,
        nullable=False,
    )

    make = Column(String(100))
    model = Column(String(100))
    year = Column(Integer)
    engine = Column(String(100))
    power = Column(String(50))
    gearbox = Column(String(50))
    vin = Column(String(17))
    mileage = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="vehicle")


# ==========================================================
# ECU
# ==========================================================

class ECU(Base):
    __tablename__ = "ecus"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        unique=True,
        nullable=False,
    )

    ecu_type = Column(String(100))
    manufacturer = Column(String(100))

    hardware = Column(String(100))
    software = Column(String(100))

    file_name = Column(String(255))
    file_path = Column(String(500))
    file_size = Column(Integer)

    checksum = Column(String(64))

    backup_path = Column(String(500))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="ecu")


# ==========================================================
# JOB
# ==========================================================

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
    )

    job_type = Column(String(100))

    status = Column(
        SQLEnum(JobStatus),
        default=JobStatus.QUEUED,
    )

    progress = Column(Float, default=0)

    started_at = Column(DateTime(timezone=True))

    finished_at = Column(DateTime(timezone=True))

    message = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="jobs")


# ==========================================================
# FILE VERSION
# ==========================================================

class FileVersion(Base):
    __tablename__ = "file_versions"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
    )

    version_number = Column(Integer, nullable=False)

    file_path = Column(String(500), nullable=False)

    file_hash = Column(String(64))

    label = Column(String(50))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="file_versions")


# ==========================================================
# AUDIT LOG
# ==========================================================

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    action = Column(String(100), nullable=False)

    resource_type = Column(String(50))

    resource_id = Column(Integer)

    details = Column(Text)

    ip_address = Column(String(45))

    created_at = Column(DateTime(timezone=True), server_default=func.now())