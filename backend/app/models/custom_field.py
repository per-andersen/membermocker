from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

VALID_FIELD_TYPES = ["string", "integer", "alphanumeric", "email", "phone", "date"]

class CustomFieldDefinition(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1)
    field_type: str
    validation_rules: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator('field_type')
    @classmethod 
    def validate_field_type(cls, v: str) -> str:
        if v not in VALID_FIELD_TYPES:
            raise ValueError(f'field_type must be one of: {", ".join(VALID_FIELD_TYPES)}')
        return v

class CustomFieldCreate(BaseModel):
    name: str = Field(..., min_length=1)
    field_type: str
    validation_rules: Dict[str, Any] = {}

    @field_validator('field_type')
    @classmethod
    def validate_field_type(cls, v: str) -> str:
        if v not in VALID_FIELD_TYPES:
            raise ValueError(f'field_type must be one of: {", ".join(VALID_FIELD_TYPES)}')
        return v

class CustomFieldValue(BaseModel):
    member_id: UUID
    field_id: UUID
    value: str

class CustomFieldUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    validation_rules: Optional[Dict[str, Any]] = None