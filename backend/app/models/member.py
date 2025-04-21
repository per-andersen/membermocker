from pydantic import BaseModel
from datetime import date


class GroupMember(BaseModel):
    date_member_joined_group: date
    first_name: str
    surname: str
    birthday: date
    phone_number: str
    email: str
    address: str