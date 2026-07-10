from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from app.services.generator import generate_members
from app.models.member import MemberConfig, Member, MemberUpdate
from app.models.custom_field import CustomFieldDefinition, CustomFieldCreate, CustomFieldUpdate, CustomFieldValue, VALID_FIELD_TYPES
from datetime import date, datetime
from app.core.config import get_db
from typing import List, Any, Optional
from uuid import UUID
from io import BytesIO
from io import StringIO
from fastapi.responses import StreamingResponse
import json
import csv


router = APIRouter()

def parse_json_field(field: Any) -> Optional[dict]:
    """Parse a field that might be a JSON string into a dictionary."""
    if isinstance(field, str):
        try:
            return json.loads(field)
        except json.JSONDecodeError:
            return None
    return field if isinstance(field, dict) else None

def custom_fields_from_json(raw: Any) -> Optional[dict]:
    """Convert a json_agg result (a list of single-entry dicts, possibly still
    JSON-encoded as a string) to a merged dict or None."""
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return None
    if isinstance(raw, list):
        result = {}
        for item in raw:
            if isinstance(item, dict):
                result.update(item)
        return result if result else None
    return None

@router.post("/generate", response_model=List[Member])
def create_members(config: MemberConfig):
    return generate_members(config)

@router.get("/members", response_model=List[Member])
def list_members(
    limit: int = Query(default=1000, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    db = get_db()
    try:
        db.execute("""
            SELECT
                m.id, m.date_member_joined_group, m.first_name, m.surname,
                m.birthday, m.phone_number, m.email, m.address,
                m.latitude, m.longitude,
                COALESCE(
                    json_agg(json_build_object(cf.name, cfv.value)) FILTER (WHERE cf.name IS NOT NULL),
                    '[]'::json
                ) as custom_fields
            FROM members m
            LEFT JOIN custom_field_values cfv ON m.id::uuid = cfv.member_id::uuid
            LEFT JOIN custom_field_definitions cf ON cfv.field_id::uuid = cf.id::uuid
            GROUP BY m.id, m.date_member_joined_group, m.first_name, m.surname,
                     m.birthday, m.phone_number, m.email, m.address, m.latitude, m.longitude
            ORDER BY m.date_member_joined_group, m.id
            LIMIT %s OFFSET %s
        """, [limit, offset])

        result = db.fetchall()
    finally:
        db.close()

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
            custom_fields=custom_fields_from_json(row[10])
        )
        for row in (result or [])
    ]

@router.get("/members/{member_id}", response_model=Member)
def get_member(member_id: UUID):
    db = get_db()
    try:
        db.execute("""
            SELECT
                m.id, m.date_member_joined_group, m.first_name, m.surname,
                m.birthday, m.phone_number, m.email, m.address,
                m.latitude, m.longitude,
                COALESCE(
                    json_agg(json_build_object(cf.name, cfv.value)) FILTER (WHERE cf.name IS NOT NULL),
                    '[]'::json
                ) as custom_fields
            FROM members m
            LEFT JOIN custom_field_values cfv ON m.id::uuid = cfv.member_id::uuid
            LEFT JOIN custom_field_definitions cf ON cfv.field_id::uuid = cf.id::uuid
            WHERE m.id::uuid = %s
            GROUP BY m.id, m.date_member_joined_group, m.first_name, m.surname,
                     m.birthday, m.phone_number, m.email, m.address, m.latitude, m.longitude
        """, [str(member_id)])

        result = db.fetchone()
    finally:
        db.close()

    if not result:
        raise HTTPException(status_code=404, detail="Member not found")

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
        custom_fields=custom_fields_from_json(result[10])
    )

@router.patch("/members/{member_id}", response_model=Member)
def update_member(member_id: UUID, member_update: MemberUpdate):
    db = get_db()
    try:
        db.execute(
            "SELECT 1 FROM members WHERE id::uuid = %s", [str(member_id)]
        )
        if not db.fetchone():
            raise HTTPException(status_code=404, detail="Member not found")

        update_fields = {
            k: v for k, v in member_update.model_dump().items()
            if v is not None and k != "custom_fields"
        }

        if update_fields:
            set_clause = ", ".join(f"{k} = %s" for k in update_fields.keys())
            values = list(update_fields.values()) + [str(member_id)]
            db.execute(f"UPDATE members SET {set_clause} WHERE id::uuid = %s", values)

        if member_update.custom_fields:
            for field_name, value in member_update.custom_fields.items():
                db.execute(
                    "SELECT id FROM custom_field_definitions WHERE name = %s",
                    [field_name],
                )
                field_result = db.fetchone()
                if field_result:
                    field_id = field_result[0]
                    db.execute(
                        "INSERT INTO custom_field_values (member_id, field_id, value) VALUES (%s, %s, %s) ON CONFLICT (member_id, field_id) DO UPDATE SET value = excluded.value",
                        [str(member_id), field_id, value],
                    )

        db.commit()
    finally:
        db.close()

    return get_member(member_id)

@router.delete("/members/{member_id}")
def delete_member(member_id: UUID):
    db = get_db()
    try:
        db.execute(
            "SELECT 1 FROM members WHERE id::uuid = %s", [str(member_id)]
        )
        if not db.fetchone():
            raise HTTPException(status_code=404, detail="Member not found")

        db.execute(
            "DELETE FROM custom_field_values WHERE member_id::uuid = %s",
            [str(member_id)],
        )
        db.execute(
            "DELETE FROM members WHERE id::uuid = %s", [str(member_id)]
        )
        db.commit()
    finally:
        db.close()

    return JSONResponse(content={"message": "Member deleted successfully"})

@router.get("/download/{format}")
def download_members(format: str):
    db = get_db()
    try:
        db.execute(
            "SELECT id, date_member_joined_group, first_name, surname, birthday, phone_number, email, address, latitude, longitude FROM members"
        )
        rows = db.fetchall()
    finally:
        db.close()

    columns = [
        "id",
        "date_member_joined_group",
        "first_name",
        "surname",
        "birthday",
        "phone_number",
        "email",
        "address",
        "latitude",
        "longitude",
    ]

    if format.lower() == "csv":
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(columns)
        writer.writerows(rows)
        response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
        response.headers["Content-Disposition"] = 'attachment; filename="members.csv"'
        return response
    elif format.lower() == "excel":
        from pandas import DataFrame

        df = DataFrame(rows, columns=columns)
        stream = BytesIO()
        df.to_excel(stream, index=False)
        response = StreamingResponse(
            iter([stream.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response.headers["Content-Disposition"] = 'attachment; filename="members.xlsx"'
        return response
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")

def _default_value_for_type(field_type: str) -> str:
    """Type-appropriate default used to backfill existing members."""
    if field_type == "number":
        return "0"
    if field_type == "date":
        return date.today().isoformat()
    if field_type == "datetime":
        return datetime.now().isoformat(timespec="minutes")
    return ""


def _validate_value_for_type(value: str, field_type: str) -> None:
    """Raise a user-friendly 422 if a value doesn't match the field type."""
    if value == "":
        return
    try:
        if field_type == "number":
            float(value)
        elif field_type == "date":
            date.fromisoformat(value)
        elif field_type == "datetime":
            datetime.fromisoformat(value)
        elif field_type == "alphanumeric":
            if not value.isalnum():
                raise ValueError
    except ValueError:
        messages = {
            "number": "The default value must be a number",
            "date": "The default value must be a date (YYYY-MM-DD)",
            "datetime": "The default value must be a date and time (YYYY-MM-DDTHH:MM)",
            "alphanumeric": "The default value may only contain letters and digits",
        }
        raise HTTPException(status_code=422, detail=messages[field_type])


@router.post("/custom-fields", response_model=CustomFieldDefinition)
def create_custom_field(field: CustomFieldCreate):
    if not field.name:
        raise HTTPException(status_code=422, detail="Field name cannot be empty")

    if field.field_type not in VALID_FIELD_TYPES:
        raise HTTPException(
            status_code=422, detail=f"Field type must be one of: {', '.join(VALID_FIELD_TYPES)}"
        )

    if field.default_value is not None:
        _validate_value_for_type(field.default_value, field.field_type)

    db = get_db()
    field_def = CustomFieldDefinition(**field.model_dump(exclude={"default_value"}))

    try:
        db.execute(
            "SELECT 1 FROM custom_field_definitions WHERE name = %s", [field_def.name]
        )
        if db.fetchone():
            raise HTTPException(
                status_code=409,
                detail=f'A field named "{field_def.name}" already exists. Please choose a different name.',
            )

        default_value = (
            field.default_value
            if field.default_value is not None
            else _default_value_for_type(field.field_type)
        )

        db.execute(
            "INSERT INTO custom_field_definitions (id, name, field_type, validation_rules, default_value) VALUES (%s, %s, %s, %s, %s)",
            [
                str(field_def.id),
                field_def.name,
                field_def.field_type,
                json.dumps(field_def.validation_rules),
                default_value,
            ],
        )

        db.execute("SELECT id FROM members")
        members = db.fetchall()
        if members:
            values = [(str(member[0]), str(field_def.id), default_value) for member in members]
            db.executemany(
                "INSERT INTO custom_field_values (member_id, field_id, value) VALUES (%s, %s, %s)",
                values,
            )

        db.commit()
    finally:
        db.close()

    return field_def

@router.get("/custom-fields", response_model=List[CustomFieldDefinition])
def list_custom_fields():
    db = get_db()
    try:
        db.execute("SELECT * FROM custom_field_definitions")
        result = db.fetchall()
    finally:
        db.close()

    return [
        CustomFieldDefinition(
            id=row[0] if isinstance(row[0], UUID) else UUID(row[0]),
            name=row[1],
            field_type=row[2],
            validation_rules=parse_json_field(row[3]) or {},
            created_at=row[4],
        )
        for row in (result or [])
    ]

@router.get("/custom-fields/{field_id}", response_model=CustomFieldDefinition)
def get_custom_field(field_id: UUID):
    db = get_db()
    try:
        db.execute(
            "SELECT * FROM custom_field_definitions WHERE id::uuid = %s", [str(field_id)]
        )
        result = db.fetchone()
    finally:
        db.close()

    if not result:
        raise HTTPException(status_code=404, detail="Custom field not found")

    return CustomFieldDefinition(
        id=result[0] if isinstance(result[0], UUID) else UUID(result[0]),
        name=result[1],
        field_type=result[2],
        validation_rules=parse_json_field(result[3]) or {},
        created_at=result[4],
    )

@router.patch("/custom-fields/{field_id}", response_model=CustomFieldDefinition)
def update_custom_field(field_id: UUID, field_update: CustomFieldUpdate):
    db = get_db()
    try:
        db.execute(
            "SELECT 1 FROM custom_field_definitions WHERE id::uuid = %s", [str(field_id)]
        )
        if not db.fetchone():
            raise HTTPException(status_code=404, detail="Custom field not found")

        update_fields = {k: v for k, v in field_update.model_dump().items() if v is not None}
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        if "validation_rules" in update_fields:
            if isinstance(update_fields["validation_rules"], str):
                try:
                    update_fields["validation_rules"] = json.dumps(
                        json.loads(update_fields["validation_rules"])
                    )
                except json.JSONDecodeError:
                    update_fields["validation_rules"] = "{}"
            else:
                update_fields["validation_rules"] = json.dumps(update_fields["validation_rules"])

        set_clause = ", ".join(f"{k} = %s" for k in update_fields.keys())
        values = list(update_fields.values()) + [str(field_id)]

        db.execute(f"UPDATE custom_field_definitions SET {set_clause} WHERE id::uuid = %s", values)
        db.commit()
    finally:
        db.close()

    return get_custom_field(field_id)

@router.delete("/custom-fields/{field_id}")
def delete_custom_field(field_id: UUID):
    db = get_db()
    try:
        db.execute(
            "SELECT 1 FROM custom_field_definitions WHERE id::uuid = %s", [str(field_id)]
        )
        if not db.fetchone():
            raise HTTPException(status_code=404, detail="Custom field not found")

        db.execute(
            "DELETE FROM custom_field_values WHERE field_id::uuid = %s", [str(field_id)]
        )
        db.execute(
            "DELETE FROM custom_field_definitions WHERE id::uuid = %s", [str(field_id)]
        )
        db.commit()
    finally:
        db.close()

    return JSONResponse(content={"message": "Custom field deleted successfully"})
