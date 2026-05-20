from fastapi.testclient import TestClient
from app.main import app
from app.core.config import get_db, TEST_DB_PATH
import pytest
import os
from app.services.generator import get_real_addresses
from uuid import uuid4
from unittest.mock import patch, MagicMock
from typing import List, Tuple
from datetime import date, timedelta
import json
import random

client = TestClient(app)

def generate_mock_member_json() -> str:
    """Generate a JSON string representing a valid Member for mocking ollama responses"""
    today = date.today()
    member_id = str(uuid4())
    
    first_names = ["John", "Jane", "Peter", "Anna", "Michael", "Sarah", "David", "Emma"]
    surnames = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
    
    first_name = random.choice(first_names)
    surname = random.choice(surnames)
    
    # Generate realistic dates
    birth_date = today - timedelta(days=random.randint(18*365, 70*365))
    join_date = today - timedelta(days=random.randint(0, 365*5))
    
    member_data = {
        "id": member_id,
        "date_member_joined_group": join_date.isoformat(),
        "first_name": first_name,
        "surname": surname,
        "birthday": birth_date.isoformat(),
        "phone_number": f"+45 {random.randint(10000000, 99999999)}",
        "email": f"{first_name.lower()}.{surname.lower()}@example.com",
        "address": "Mock Address",
        "latitude": None,
        "longitude": None,
        "custom_fields": None
    }
    
    return json.dumps(member_data)

def mock_ollama_chat(*args, **kwargs):
    """Mock function for ollama.chat that returns valid member data"""
    response = MagicMock()
    response.message.content = generate_mock_member_json()
    return response

def mock_get_real_addresses(city: str, country: str, count: int) -> List[Tuple[str, float, float]]:
    """
    Mock function that returns fake addresses for testing.
    Returns addresses with consistent, predictable coordinates.
    """
    addresses = []
    for i in range(count):
        address = f"Vej {i+1}, 1000 {city}, {country}"
        latitude = 55.6761 + (i * 0.0001)  # Slight variations
        longitude = 12.5683 + (i * 0.0001)
        addresses.append((address, latitude, longitude))
    return addresses

@pytest.fixture
def mock_addresses(request):
    """
    Fixture that patches get_real_addresses with mock implementation.
    Only applies the patch if --run-expensive is NOT specified.
    If --run-expensive is used, the real API will be called.
    """
    run_expensive = request.config.getoption("--run-expensive")
    
    if run_expensive:
        # Use real API calls
        yield
    else:
        # Use mocked addresses - patch both the module and the import location
        with patch('app.services.generator.get_real_addresses', side_effect=mock_get_real_addresses):
            with patch('test_api.get_real_addresses', side_effect=mock_get_real_addresses):
                yield

@pytest.fixture
def mock_chat(request):
    """
    Fixture that patches ollama.chat with mock implementation.
    Only applies the patch if --run-expensive is NOT specified.
    If --run-expensive is used, the real ollama chat will be called.
    """
    run_expensive = request.config.getoption("--run-expensive")
    
    if run_expensive:
        # Use real ollama chat
        yield
    else:
        # Use mocked chat
        with patch('app.services.generator.chat', side_effect=mock_ollama_chat):
            yield

@pytest.fixture(autouse=True)
def test_db():
    try:
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()

        os.environ["TESTING"] = "1"
        
        db = get_db()
        
        yield db

    finally:
        if 'db' in locals():
            db.close()
        
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()
        
        if "TESTING" in os.environ:
            del os.environ["TESTING"]

def test_generate_members(test_db, mock_addresses, mock_chat):
    response = client.post("/generate", json={
        "city": "Copenhagen",
        "country": "Denmark",
        "count": 2,
        "min_age": 20,
        "max_age": 30
    })
    assert response.status_code == 200
    members = response.json()
    assert len(members) == 2
    for member in members:
        assert "id" in member
        assert "first_name" in member
        assert "surname" in member
        assert "email" in member
        assert "phone_number" in member
        assert "address" in member

def test_list_members(test_db, mock_addresses, mock_chat):
    
    client.post("/generate", json={
        "city": "Copenhagen",
        "country": "Denmark",
        "count": 3
    })
    
    response = client.get("/members")
    assert response.status_code == 200
    members = response.json()
    assert len(members) == 3

def test_get_member(test_db, mock_addresses, mock_chat):
    
    response = client.post("/generate", json={
        "city": "Copenhagen",
        "country": "Denmark",
        "count": 1
    })
    member_id = response.json()[0]["id"]
    
    response = client.get(f"/members/{member_id}")
    assert response.status_code == 200
    member = response.json()
    assert member["id"] == member_id


def test_update_member(test_db, mock_addresses, mock_chat):
    
    response = client.post("/generate", json={
        "city": "Copenhagen",
        "country": "Denmark",
        "count": 1
    })
    member_id = response.json()[0]["id"]
    
    update_data = {
        "first_name": "Updated",
        "surname": "Name"
    }
    
    response = client.patch(f"/members/{member_id}", json=update_data)
    assert response.status_code == 200
    updated_member = response.json()
    assert updated_member["first_name"] == "Updated"
    assert updated_member["surname"] == "Name"

def test_delete_member(test_db, mock_addresses, mock_chat):
    response = client.post("/generate", json={
        "city": "Copenhagen",
        "country": "Denmark",
        "count": 1
    })
    member_id = response.json()[0]["id"]
    
    response = client.delete(f"/members/{member_id}")
    assert response.status_code == 200
    
    response = client.get(f"/members/{member_id}")
    assert response.status_code == 404

def test_download_members(test_db, mock_addresses, mock_chat):
    client.post("/generate", json={
        "city": "Copenhagen",
        "country": "Denmark",
        "count": 2
    })

    response = client.get("/download/csv")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "content-disposition" in response.headers
    
    response = client.get("/download/excel")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert "content-disposition" in response.headers

    response = client.get("/download/invalid")
    assert response.status_code == 400

def test_get_real_addresses(mock_addresses):
    city = "København"
    country = "Danmark"
    count = 10

    addresses = get_real_addresses(city, country, count)
    assert len(addresses) == count
    for address in addresses:
        assert "København" in address[0]
        assert "Danmark" in address[0]

def test_create_custom_field(test_db):
    """Test creating a custom field"""
    field_data = {
        "name": "membership_level",
        "field_type": "string",
        "validation_rules": {
            "min_length": 2,
            "max_length": 20
        }
    }
    
    response = client.post("/custom-fields", json=field_data)
    assert response.status_code == 200
    created_field = response.json()
    assert created_field["name"] == field_data["name"]
    assert created_field["field_type"] == field_data["field_type"]
    assert created_field["validation_rules"] == field_data["validation_rules"]

def test_list_custom_fields(test_db):
    fields = [
        {
            "name": "membership_level",
            "field_type": "string",
            "validation_rules": {"min_length": 2}
        },
        {
            "name": "points",
            "field_type": "integer",
            "validation_rules": {"min": 0}
        }
    ]
    
    for field in fields:
        client.post("/custom-fields", json=field)
    
    response = client.get("/custom-fields")
    assert response.status_code == 200
    listed_fields = response.json()
    assert len(listed_fields) >= 2
    assert {f["name"] for f in listed_fields} == {"membership_level", "points"}

def test_update_custom_field(test_db):
    field_data = {
        "name": "membership_level",
        "field_type": "string",
        "validation_rules": {"min_length": 2}
    }
    
    create_response = client.post("/custom-fields", json=field_data)
    field_id = create_response.json()["id"]
    
    update_data = {
        "name": "member_level",
        "validation_rules": {"min_length": 3, "max_length": 20}
    }
    
    response = client.patch(f"/custom-fields/{field_id}", json=update_data)
    assert response.status_code == 200
    updated_field = response.json()
    assert updated_field["name"] == update_data["name"]
    assert updated_field["validation_rules"] == update_data["validation_rules"]

def test_delete_custom_field(test_db):
    field_data = {
        "name": "membership_level",
        "field_type": "string",
        "validation_rules": {}
    }
    
    create_response = client.post("/custom-fields", json=field_data)
    field_id = create_response.json()["id"]
    
    response = client.delete(f"/custom-fields/{field_id}")
    assert response.status_code == 200
    
    get_response = client.get(f"/custom-fields/{field_id}")
    assert get_response.status_code == 404

def test_member_with_custom_fields(test_db, mock_addresses, mock_chat):
    field_data = {
        "name": "membership_level",
        "field_type": "string",
        "validation_rules": {}
    }
    client.post("/custom-fields", json=field_data)
    
    response = client.post("/generate", json={
        "city": "Copenhagen",
        "country": "Denmark",
        "count": 1
    })
    member = response.json()[0]
    
    update_data = {
        "custom_fields": {
            "membership_level": "gold"
        }
    }
    
    response = client.patch(f"/members/{member['id']}", json=update_data)
    assert response.status_code == 200
    updated_member = response.json()
    assert updated_member["custom_fields"] == update_data["custom_fields"]
    
    response = client.get(f"/members/{member['id']}")
    assert response.status_code == 200
    retrieved_member = response.json()
    assert retrieved_member["custom_fields"] == update_data["custom_fields"]

def test_invalid_member_data(test_db, mock_addresses, mock_chat):
    """Test handling of invalid member data"""
    invalid_id = str(uuid4())
    
    response = client.get(f"/members/{invalid_id}")
    assert response.status_code == 404
    
    response = client.patch(f"/members/{invalid_id}", json={"first_name": "Test"})
    assert response.status_code == 404
    
    response = client.delete(f"/members/{invalid_id}")
    assert response.status_code == 404
    
    response = client.post("/generate", json={
        "city": "Copenhagen",
        "country": "Denmark",
        "count": 101  # Exceeds maximum allowed
    })
    assert response.status_code == 422

def test_invalid_custom_field_data(test_db):
    """Test handling of invalid custom field operations"""
    invalid_id = str(uuid4())
    
    response = client.get(f"/custom-fields/{invalid_id}")
    assert response.status_code == 404
    
    response = client.patch(f"/custom-fields/{invalid_id}", json={"name": "test"})
    assert response.status_code == 404
    
    response = client.delete(f"/custom-fields/{invalid_id}")
    assert response.status_code == 404
    
    response = client.post("/custom-fields", json={
        "name": "",  # Empty name
        "field_type": "invalid_type",
        "validation_rules": {}
    })
    assert response.status_code == 422
