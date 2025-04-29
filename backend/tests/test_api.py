from fastapi.testclient import TestClient
from app.main import app
from app.core.config import get_db, TEST_DB_PATH
import pytest
import os
from app.services.generator import get_real_addresses
from uuid import uuid4

client = TestClient(app)

@pytest.fixture(autouse=True)
def test_db():
    try:
        """Set up test database for each test"""
        # Clean up any existing test database
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()

        # Set environment to use test database
        os.environ["TESTING"] = "1"
        
        # Get DB connection - this will create tables
        db = get_db()
        
        yield db

    finally:
        # Ensure the database is closed
        if 'db' in locals():
            db.close()
        # Remove test database
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()
        # Remove testing environment variable
        if "TESTING" in os.environ:
            del os.environ["TESTING"]

def test_generate_members(test_db):
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

def test_list_members(test_db):
    # First generate some members
    client.post("/generate", json={
        "city": "Copenhagen",
        "country": "Denmark",
        "count": 3
    })
    
    response = client.get("/members")
    assert response.status_code == 200
    members = response.json()
    assert len(members) == 3  # Now we can assert exact count since we have test isolation

def test_get_member(test_db):
    # First generate a member
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

def test_update_member(test_db):
    # First generate a member
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

def test_delete_member(test_db):
    # First generate a member
    response = client.post("/generate", json={
        "city": "Copenhagen",
        "country": "Denmark",
        "count": 1
    })
    member_id = response.json()[0]["id"]
    
    response = client.delete(f"/members/{member_id}")
    assert response.status_code == 200
    
    # Verify member is deleted
    response = client.get(f"/members/{member_id}")
    assert response.status_code == 404

def test_download_members(test_db):
    # First generate some members
    client.post("/generate", json={
        "city": "Copenhagen",
        "country": "Denmark",
        "count": 2
    })

    # Test CSV download
    response = client.get("/download/csv")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "content-disposition" in response.headers
    
    # Test Excel download
    response = client.get("/download/excel")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert "content-disposition" in response.headers

    # Test invalid format
    response = client.get("/download/invalid")
    assert response.status_code == 400

def test_get_real_addresses():
    # Test with a known city and country
    city = "København"
    country = "Danmark"
    count = 10

    addresses = get_real_addresses(city, country, count)
    assert len(addresses) == count
    for address in addresses:
        assert "københavn" in address[0].lower()
        assert "danmark" in address[0].lower()

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
    """Test listing custom fields"""
    # Create two custom fields
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
    assert len(listed_fields) == 2
    assert {f["name"] for f in listed_fields} == {"membership_level", "points"}

def test_update_custom_field(test_db):
    """Test updating a custom field"""
    # Create a custom field
    field_data = {
        "name": "membership_level",
        "field_type": "string",
        "validation_rules": {"min_length": 2}
    }
    
    create_response = client.post("/custom-fields", json=field_data)
    field_id = create_response.json()["id"]
    
    # Update the field
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
    """Test deleting a custom field"""
    # Create a custom field
    field_data = {
        "name": "membership_level",
        "field_type": "string",
        "validation_rules": {}
    }
    
    create_response = client.post("/custom-fields", json=field_data)
    field_id = create_response.json()["id"]
    
    # Delete the field
    response = client.delete(f"/custom-fields/{field_id}")
    assert response.status_code == 200
    
    # Verify field is deleted
    get_response = client.get(f"/custom-fields/{field_id}")
    assert get_response.status_code == 404

def test_member_with_custom_fields(test_db):
    """Test creating and updating members with custom fields"""
    # Create a custom field
    field_data = {
        "name": "membership_level",
        "field_type": "string",
        "validation_rules": {}
    }
    client.post("/custom-fields", json=field_data)
    
    # Generate a member
    response = client.post("/generate", json={
        "city": "Copenhagen",
        "country": "Denmark",
        "count": 1
    })
    member = response.json()[0]
    
    # Update member with custom field
    update_data = {
        "custom_fields": {
            "membership_level": "gold"
        }
    }
    
    response = client.patch(f"/members/{member['id']}", json=update_data)
    assert response.status_code == 200
    updated_member = response.json()
    assert updated_member["custom_fields"] == update_data["custom_fields"]
    
    # Verify custom field is returned when getting member
    response = client.get(f"/members/{member['id']}")
    assert response.status_code == 200
    retrieved_member = response.json()
    assert retrieved_member["custom_fields"] == update_data["custom_fields"]

def test_invalid_member_data(test_db):
    """Test handling of invalid member data"""
    invalid_id = str(uuid4())
    
    # Test getting non-existent member
    response = client.get(f"/members/{invalid_id}")
    assert response.status_code == 404
    
    # Test updating non-existent member
    response = client.patch(f"/members/{invalid_id}", json={"first_name": "Test"})
    assert response.status_code == 404
    
    # Test deleting non-existent member
    response = client.delete(f"/members/{invalid_id}")
    assert response.status_code == 404
    
    # Test invalid member generation config
    response = client.post("/generate", json={
        "city": "Copenhagen",
        "country": "Denmark",
        "count": 101  # Exceeds maximum allowed
    })
    assert response.status_code == 422

def test_invalid_custom_field_data(test_db):
    """Test handling of invalid custom field operations"""
    invalid_id = str(uuid4())
    
    # Test getting non-existent custom field
    response = client.get(f"/custom-fields/{invalid_id}")
    assert response.status_code == 404
    
    # Test updating non-existent custom field
    response = client.patch(f"/custom-fields/{invalid_id}", json={"name": "test"})
    assert response.status_code == 404
    
    # Test deleting non-existent custom field
    response = client.delete(f"/custom-fields/{invalid_id}")
    assert response.status_code == 404
    
    # Test creating custom field with invalid data
    response = client.post("/custom-fields", json={
        "name": "",  # Empty name
        "field_type": "invalid_type",
        "validation_rules": {}
    })
    assert response.status_code == 422

