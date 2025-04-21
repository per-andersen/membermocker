from ollama import chat
from faker import Faker
from app.models.member import MemberConfig, Member


def generate_members(config: MemberConfig):
    response = chat(
        messages=[
            {
                'role': 'user',
                'content': f'Get the data for this ficticious group member from the city of {config.city}, {config.country}.',
            }
        ],
        model='llama3.1',
        format=Member.model_json_schema(),
    )

    group_member = Member.model_validate_json(response.message.content)
    return group_member
