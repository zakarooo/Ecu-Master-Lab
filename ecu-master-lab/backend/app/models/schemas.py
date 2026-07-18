import re
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime

_PASSWORD_RE = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Adresse email invalide")
        return v.lower().strip()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not _PASSWORD_RE.match(v):
            raise ValueError(
                "Le mot de passe doit contenir au moins 8 caractères, "
                "une majuscule, une minuscule et un chiffre"
            )
        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if len(v.strip()) < 2:
            raise ValueError("Le nom doit contenir au moins 2 caractères")
        return v.strip()


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ProjectCreate(BaseModel):
    name: str
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_year: Optional[int] = None
    vehicle_engine: Optional[str] = None
    vehicle_power: Optional[str] = None
    vehicle_ecu_type: Optional[str] = None
    vehicle_mileage: Optional[int] = None
    vehicle_gearbox: Optional[str] = None
    vehicle_vin: Optional[str] = None
    tool_used: Optional[str] = None


class ModificationSelect(BaseModel):
    modifications: List[str]
    client_notes: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    status: str
    vehicle_make: Optional[str]
    vehicle_model: Optional[str]
    vehicle_year: Optional[int]
    vehicle_engine: Optional[str]
    vehicle_power: Optional[str]
    vehicle_ecu_type: Optional[str]
    ecu_filename: Optional[str]
    ai_detected_ecu: Optional[str]
    ai_detected_hw: Optional[str]
    ai_detected_sw: Optional[str]
    ai_checksum_valid: Optional[bool]
    ai_confidence: Optional[float]
    ai_analysis_json: Optional[str]
    modifications: Optional[str]
    client_notes: Optional[str]
    result_file_path: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AdminStats(BaseModel):
    total_users: int
    total_projects: int
    pending_projects: int
    completed_projects: int
    analyzing_projects: int
    failed_projects: int


class AdminUserUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None
