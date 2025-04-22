from pydantic import BaseModel, Field, Json
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

class CustomFieldDefinition(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    field_type: str  # e.g. 'integer', 'string', 'alphanumeric'
    validation_rules: Dict[str, Any]  # e.g. {'min_length': 5, 'max_length': 10}
    created_at: datetime = Field(default_factory=datetime.now)

class CustomFieldCreate(BaseModel):
    name: str
    field_type: str
    validation_rules: Dict[str, Any]

class CustomFieldValue(BaseModel):
    member_id: UUID
    field_id: UUID
    value: str

class CustomFieldUpdate(BaseModel):
    name: Optional[str] = None
    validation_rules: Optional[Dict[str, Any]] = None