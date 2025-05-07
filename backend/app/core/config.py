import duckdb
from pathlib import Path
import os

DB_PATH = Path(__file__).parent.parent.parent / "data" / "members.duckdb"
TEST_DB_PATH = Path(__file__).parent.parent.parent / "data" / "test_members.duckdb"

def get_db():
    db_path = TEST_DB_PATH if os.getenv("TESTING") else DB_PATH
    db_path.parent.mkdir(exist_ok=True)
    
    conn = duckdb.connect(str(db_path))

    # Even though the below tables were previously created with 'IF NOT EXISTS' exceptions of type:
    # 'duckdb.duckdb.TransactionException: TransactionContext Error: Catalog write-write conflict on alter with "members"'
    # would be raised when running the app. Therefore we first create a table to keep track of what we've created,
    # and only create the tables if they don't exist. A sort of 'IF NOT EXISTS' done by hand. Once DuckDB supports 
    # ALTER TABLE for adding FOREIGN KEY constraints, we can remove this workaround and implement a more siccint solution
    # using the duckdb_constraints() metadata function.
    
    tables = conn.execute("SELECT table_name FROM duckdb_tables() WHERE schema_name = 'main'").fetchall()
    existing_tables = [t[0] for t in tables]
    
    if 'members' not in existing_tables:
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
    
    if 'custom_field_definitions' not in existing_tables:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS custom_field_definitions (
                id UUID PRIMARY KEY,
                name VARCHAR NOT NULL,
                field_type VARCHAR NOT NULL,
                validation_rules JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    if 'custom_field_values' not in existing_tables:
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

if __name__ == "__main__":
   conn = get_db()
   existing_constraints = conn.execute("""
        SELECT constraint_name
        FROM duckdb_constraints()
        WHERE table_name = 'custom_field_values'
    """).fetchall()
   print(existing_constraints)