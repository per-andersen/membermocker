from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.services.generator import generate_members
from app.models.member import MemberConfig, Member, MemberUpdate
from app.core.config import get_db
from typing import List
from uuid import UUID
from io import BytesIO
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.post("/generate", response_model=List[Member])
def create_members(config: MemberConfig):
    return generate_members(config)

@router.get("/members", response_model=List[Member])
def list_members():
    db = get_db()
    result = db.execute("SELECT * FROM members").fetchall()
    # Return empty list instead of error when no members exist
    return [
        Member(
            id=row[0] if isinstance(row[0], UUID) else UUID(row[0]),
            date_member_joined_group=row[1],
            first_name=row[2],
            surname=row[3],
            birthday=row[4],
            phone_number=row[5],
            email=row[6],
            address=row[7]
        )
        for row in (result or [])
    ]

@router.get("/members/{member_id}", response_model=Member)
def get_member(member_id: UUID):
    db = get_db()
    result = db.execute("SELECT * FROM members WHERE id = ?", [str(member_id)]).fetchone()
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
        address=result[7]
    )

@router.patch("/members/{member_id}", response_model=Member)
def update_member(member_id: UUID, member_update: MemberUpdate):
    db = get_db()
    # First check if member exists
    if not db.execute("SELECT 1 FROM members WHERE id = ?", [str(member_id)]).fetchone():
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Build update query dynamically based on provided fields
    update_fields = {k: v for k, v in member_update.model_dump().items() if v is not None}
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    set_clause = ", ".join(f"{k} = ?" for k in update_fields.keys())
    values = list(update_fields.values())
    values.append(str(member_id))
    
    db.execute(f"UPDATE members SET {set_clause} WHERE id = ?", values)
    
    # Return updated member
    return get_member(member_id)

@router.delete("/members/{member_id}")
def delete_member(member_id: UUID):
    db = get_db()
    if not db.execute("SELECT 1 FROM members WHERE id = ?", [str(member_id)]).fetchone():
        raise HTTPException(status_code=404, detail="Member not found")
    
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