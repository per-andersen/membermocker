from fastapi.testclient import TestClient
from app.main import app
from app.core.config import get_db
from app.services.generator import get_real_addresses
import pytest

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_db():
    # Clear the test database before each test
    db = get_db()
    db.execute("DELETE FROM members")
    yield
    db.execute("DELETE FROM members")

def test_generate_members():
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

def test_list_members():
    # First generate some members
    client.post("/generate", json={
        "city": "Copenhagen",
        "country": "Denmark",
        "count": 3
    })
    
    response = client.get("/members")
    assert response.status_code == 200
    members = response.json()
    assert len(members) >= 3

def test_get_member():
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

def test_update_member():
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

def test_delete_member():
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

def test_download_members():
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
        assert "københavn" in address.lower()
        assert "danmark" in address.lower()
        
    