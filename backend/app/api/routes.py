from fastapi import APIRouter
from app.services.generator import generate_members
from app.models.member import MemberConfig

router = APIRouter()

@router.post("/generate")
def create_members(config: MemberConfig):
    return generate_members(config)