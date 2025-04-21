from ollama import chat
from app.models.member import MemberConfig, Member
from app.core.config import get_db
from typing import List

def generate_members(config: MemberConfig) -> List[Member]:
    members = []
    for _ in range(config.count):
        response = chat(
            messages=[
                {
                    'role': 'user',
                    'content': f'Get the data for this ficticious group member from the city of {config.city}, {config.country}. Their age should be between {config.min_age} and {config.max_age} years old.',
                }
            ],
            model='llama3.1',
            format=Member.model_json_schema(),
        )
        
        member = Member.model_validate_json(response.message.content)
        members.append(member)
    
    # Store in database
    db = get_db()
    for member in members:
        db.execute("""
            INSERT INTO members 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            str(member.id),
            member.date_member_joined_group,
            member.first_name,
            member.surname,
            member.birthday,
            member.phone_number,
            member.email,
            member.address
        ])
    
    return members
