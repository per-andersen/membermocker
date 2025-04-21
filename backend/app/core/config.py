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
            address VARCHAR
        )
    """)
    return conn