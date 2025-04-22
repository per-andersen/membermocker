import duckdb
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "members.duckdb"
DB_PATH.parent.mkdir(exist_ok=True)

def get_db():
    conn = duckdb.connect(str(DB_PATH))
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