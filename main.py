from ollama import chat
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


if __name__ == "__main__":
    for ii in range(100):
        generate_fake_group_member()
