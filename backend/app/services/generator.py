from ollama import chat
from faker import Faker
from app.models.member import MemberConfig

def generate_members(config: MemberConfig):
    fake = Faker(config.country)
    members = []
    for _ in range(config.count):
        members.append({
            "name": fake.name(),
            "email": fake.email(),
            "address": fake.address()
        })
    return members


def generate_fake_group_member():
    response = chat(
        messages=[
            {
                'role': 'user',
                'content': 'Get the data for this ficticious group member from the city of Copenhagen, Denmark.',
            }
        ],
        model='llama3.1',
        format=GroupMember.model_json_schema(),
    )

    group_member = GroupMember.model_validate_json(response.message.content)
    print(group_member)
