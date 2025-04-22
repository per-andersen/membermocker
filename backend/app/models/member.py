from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, Dict
from uuid import UUID, uuid4

class MemberConfig(BaseModel):
    city: str
    country: str
    count: int = Field(default=1, ge=1, le=100)
    min_age: int = Field(default=18, ge=0, le=120)
    max_age: int = Field(default=90, ge=0, le=120)

class Member(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    date_member_joined_group: date
    first_name: str
    surname: str
    birthday: date
    phone_number: str
    email: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    custom_fields: Optional[Dict[str, str]] = None

class MemberUpdate(BaseModel):
    date_member_joined_group: Optional[date] = None
    first_name: Optional[str] = None
    surname: Optional[str] = None
    birthday: Optional[date] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    custom_fields: Optional[Dict[str, str]] = None