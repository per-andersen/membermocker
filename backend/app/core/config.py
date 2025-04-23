import duckdb
from pathlib import Path
import os

# Default to production database
DB_PATH = Path(__file__).parent.parent.parent / "data" / "members.duckdb"
TEST_DB_PATH = Path(__file__).parent.parent.parent / "data" / "test_members.duckdb"

def get_db():
    # Use test database if TESTING environment variable is set
    db_path = TEST_DB_PATH if os.getenv("TESTING") else DB_PATH
    db_path.parent.mkdir(exist_ok=True)
    
    conn = duckdb.connect(str(db_path))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id UUID PRIMARY KEY,
            date_member_joined_group DATE,
            first_name VARCHAR,
            surname VARCHAR,
            birthday DATE,
            phone_number VARCHAR,
            email VARCHAR,
            address VARCHAR,
            latitude DOUBLE,
            longitude DOUBLE
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS custom_field_definitions (
            id UUID PRIMARY KEY,
            name VARCHAR NOT NULL,
            field_type VARCHAR NOT NULL,
            validation_rules JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS custom_field_values (
            member_id UUID,
            field_id UUID,
            value VARCHAR,
            PRIMARY KEY (member_id, field_id),
            FOREIGN KEY (member_id) REFERENCES members(id),
            FOREIGN KEY (field_id) REFERENCES custom_field_definitions(id)
        )
    """)
    return conn