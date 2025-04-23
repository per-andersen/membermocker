from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.services.generator import generate_members
from app.models.member import MemberConfig, Member, MemberUpdate
from app.models.custom_field import CustomFieldDefinition, CustomFieldCreate, CustomFieldUpdate, CustomFieldValue
from app.core.config import get_db
from typing import List, Any, Optional
from uuid import UUID
from io import BytesIO
from fastapi.responses import StreamingResponse
import json

router = APIRouter()

def parse_json_field(field: Any) -> Optional[dict]:
    """Parse a field that might be a JSON string into a dictionary."""
    if isinstance(field, str):
        try:
            return json.loads(field)
        except json.JSONDecodeError:
            return None
    return field if isinstance(field, dict) else None

@router.post("/generate", response_model=List[Member])
def create_members(config: MemberConfig):
    return generate_members(config)

@router.get("/members", response_model=List[Member])
def list_members():
    db = get_db()
    members_result = db.execute("""
        SELECT m.*, json_group_object(cf.name, cfv.value) as custom_fields
        FROM members m
        LEFT JOIN custom_field_values cfv ON m.id = cfv.member_id
        LEFT JOIN custom_field_definitions cf ON cfv.field_id = cf.id
        GROUP BY m.id, m.date_member_joined_group, m.first_name, m.surname, 
                 m.birthday, m.phone_number, m.email, m.address, m.latitude, m.longitude
    """).fetchall()
    
    return [
        Member(
            id=row[0] if isinstance(row[0], UUID) else UUID(row[0]),
            date_member_joined_group=row[1],
            first_name=row[2],
            surname=row[3],
            birthday=row[4],
            phone_number=row[5],
            email=row[6],
            address=row[7],
            latitude=row[8],
            longitude=row[9],
            custom_fields=parse_json_field(row[10]) if row[10] != '{}' else None
        )
        for row in (members_result or [])
    ]

@router.get("/members/{member_id}", response_model=Member)
def get_member(member_id: UUID):
    db = get_db()
    result = db.execute("""
        SELECT m.*, json_group_object(cf.name, cfv.value) as custom_fields
        FROM members m
        LEFT JOIN custom_field_values cfv ON m.id = cfv.member_id
        LEFT JOIN custom_field_definitions cf ON cfv.field_id = cf.id
        WHERE m.id = ?
        GROUP BY m.id, m.date_member_joined_group, m.first_name, m.surname, 
                 m.birthday, m.phone_number, m.email, m.address, m.latitude, m.longitude
    """, [str(member_id)]).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Member not found")
    
    custom_fields = parse_json_field(result[10])
    
    return Member(
        id=result[0] if isinstance(result[0], UUID) else UUID(result[0]),
        date_member_joined_group=result[1],
        first_name=result[2],
        surname=result[3],
        birthday=result[4],
        phone_number=result[5],
        email=result[6],
        address=result[7],
        latitude=result[8],
        longitude=result[9],
        custom_fields=custom_fields if custom_fields != '{}' else None
    )

@router.patch("/members/{member_id}", response_model=Member)
def update_member(member_id: UUID, member_update: MemberUpdate):
    db = get_db()
    
    if not db.execute("SELECT 1 FROM members WHERE id = ?", [str(member_id)]).fetchone():
        raise HTTPException(status_code=404, detail="Member not found")
    
    
    update_fields = {k: v for k, v in member_update.model_dump().items() 
                    if v is not None and k != 'custom_fields'}
    
    if update_fields:
        set_clause = ", ".join(f"{k} = ?" for k in update_fields.keys())
        values = list(update_fields.values())
        values.append(str(member_id))
        db.execute(f"UPDATE members SET {set_clause} WHERE id = ?", values)
    
    
    if member_update.custom_fields:
        for field_name, value in member_update.custom_fields.items():
            
            field_result = db.execute(
                "SELECT id FROM custom_field_definitions WHERE name = ?", 
                [field_name]
            ).fetchone()
            
            if field_result:
                field_id = field_result[0]
                db.execute("""
                    INSERT INTO custom_field_values (member_id, field_id, value)
                    VALUES (?, ?, ?)
                    ON CONFLICT (member_id, field_id) DO UPDATE SET value = excluded.value
                """, [str(member_id), field_id, value])
    
    return get_member(member_id)

@router.delete("/members/{member_id}")
def delete_member(member_id: UUID):
    db = get_db()
    if not db.execute("SELECT 1 FROM members WHERE id = ?", [str(member_id)]).fetchone():
        raise HTTPException(status_code=404, detail="Member not found")
    
    
    db.execute("DELETE FROM custom_field_values WHERE member_id = ?", [str(member_id)])
    
    db.execute("DELETE FROM members WHERE id = ?", [str(member_id)])
    return JSONResponse(content={"message": "Member deleted successfully"})

@router.get("/download/{format}")
def download_members(format: str):
    db = get_db()
    df = db.execute("SELECT * FROM members").df()
    
    if format.lower() == "csv":
        stream = BytesIO()
        df.to_csv(stream, index=False)
        response = StreamingResponse(
            iter([stream.getvalue()]), 
            media_type="text/csv"
        )
        response.headers["Content-Disposition"] = 'attachment; filename="members.csv"'
        return response
    elif format.lower() == "excel":
        stream = BytesIO()
        df.to_excel(stream, index=False)
        response = StreamingResponse(
            iter([stream.getvalue()]), 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response.headers["Content-Disposition"] = 'attachment; filename="members.xlsx"'
        return response
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")

@router.post("/custom-fields", response_model=CustomFieldDefinition)
def create_custom_field(field: CustomFieldCreate):
    if not field.name:
        raise HTTPException(status_code=422, detail="Field name cannot be empty")
        
    valid_field_types = ["string", "integer", "alphanumeric", "email", "phone", "date"]
    if field.field_type not in valid_field_types:
        raise HTTPException(status_code=422, detail=f"Field type must be one of: {', '.join(valid_field_types)}")
        
    db = get_db()
    field_def = CustomFieldDefinition(**field.model_dump())
    
    db.execute("""
        INSERT INTO custom_field_definitions (id, name, field_type, validation_rules)
        VALUES (?, ?, ?, ?)
    """, [str(field_def.id), field_def.name, field_def.field_type, field_def.validation_rules])
    
    
    members = db.execute("SELECT id FROM members").fetchall()
    if members:
        
        default_value = ""  # TODO: Make this more sophisticated based on field type
        values = [(str(member[0]), str(field_def.id), default_value) for member in members]
        db.executemany("""
            INSERT INTO custom_field_values (member_id, field_id, value)
            VALUES (?, ?, ?)
        """, values)
    
    return field_def

@router.get("/custom-fields", response_model=List[CustomFieldDefinition])
def list_custom_fields():
    db = get_db()
    result = db.execute("SELECT * FROM custom_field_definitions").fetchall()
    
    return [
        CustomFieldDefinition(
            id=row[0] if isinstance(row[0], UUID) else UUID(row[0]),
            name=row[1],
            field_type=row[2],
            validation_rules=parse_json_field(row[3]) or {},
            created_at=row[4]
        )
        for row in (result or [])
    ]

@router.get("/custom-fields/{field_id}", response_model=CustomFieldDefinition)
def get_custom_field(field_id: UUID):
    db = get_db()
    result = db.execute("SELECT * FROM custom_field_definitions WHERE id = ?", [str(field_id)]).fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Custom field not found")
    
    return CustomFieldDefinition(
        id=result[0] if isinstance(result[0], UUID) else UUID(result[0]),
        name=result[1],
        field_type=result[2],
        validation_rules=parse_json_field(result[3]) or {},
        created_at=result[4]
    )

@router.patch("/custom-fields/{field_id}", response_model=CustomFieldDefinition)
def update_custom_field(field_id: UUID, field_update: CustomFieldUpdate):
    db = get_db()
    if not db.execute("SELECT 1 FROM custom_field_definitions WHERE id = ?", [str(field_id)]).fetchone():
        raise HTTPException(status_code=404, detail="Custom field not found")
    
    update_fields = {k: v for k, v in field_update.model_dump().items() if v is not None}
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    if 'validation_rules' in update_fields:
        if isinstance(update_fields['validation_rules'], str):
            try:
                update_fields['validation_rules'] = json.dumps(json.loads(update_fields['validation_rules']))
            except json.JSONDecodeError:
                update_fields['validation_rules'] = '{}'
        else:
            update_fields['validation_rules'] = json.dumps(update_fields['validation_rules'])
    
    set_clause = ", ".join(f"{k} = ?" for k in update_fields.keys())
    values = list(update_fields.values())
    values.append(str(field_id))
    
    db.execute(f"UPDATE custom_field_definitions SET {set_clause} WHERE id = ?", values)
    
    return get_custom_field(field_id)

@router.delete("/custom-fields/{field_id}")
def delete_custom_field(field_id: UUID):
    db = get_db()
    if not db.execute("SELECT 1 FROM custom_field_definitions WHERE id = ?", [str(field_id)]).fetchone():
        raise HTTPException(status_code=404, detail="Custom field not found")
    
    db.execute("DELETE FROM custom_field_values WHERE field_id = ?", [str(field_id)])
    db.execute("DELETE FROM custom_field_definitions WHERE id = ?", [str(field_id)])
    return JSONResponse(content={"message": "Custom field deleted successfully"})