import os
import threading
from psycopg import Connection
from psycopg_pool import ConnectionPool


_pool: ConnectionPool | None = None
_pool_lock = threading.Lock()


def _conninfo() -> str:
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    dbname = os.getenv("DB_NAME", "membermocker")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres")
    sslmode = os.getenv("DB_SSLMODE", "disable")

    return f"host={host} port={port} dbname={dbname} user={user} password={password} sslmode={sslmode}"


def _get_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        with _pool_lock:
            if _pool is None:
                pool = ConnectionPool(_conninfo(), min_size=1, max_size=10, open=False)
                pool.open(wait=True, timeout=30)
                with pool.connection() as conn:
                    _initialize_tables(conn)
                _pool = pool
    return _pool


class SimpleDB:
    """A thin wrapper around a pooled psycopg3 connection for simple SQL operations."""

    def __init__(self, pool: ConnectionPool):
        self._pool = pool
        self._conn = pool.getconn()
        self._cursor = self._conn.cursor()

    def execute(self, sql: str, params: list = None):
        if params is None:
            params = []
        self._cursor.execute(sql, params)

    def executemany(self, sql: str, params_list: list):
        self._cursor.executemany(sql, params_list)

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def commit(self):
        self._conn.commit()

    def close(self):
        self._cursor.close()
        # Discard any uncommitted state before handing the connection back
        self._conn.rollback()
        self._pool.putconn(self._conn)


def get_db() -> SimpleDB:
    """Get a database handle backed by the shared connection pool."""
    return SimpleDB(_get_pool())


def _initialize_tables(conn: Connection) -> None:
    """Initialize database tables if they don't exist."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id UUID PRIMARY KEY,
                date_member_joined_group DATE NOT NULL,
                first_name VARCHAR(100) NOT NULL,
                surname VARCHAR(100) NOT NULL,
                birthday DATE NOT NULL,
                phone_number VARCHAR(50) NOT NULL,
                email VARCHAR(255) NOT NULL,
                address TEXT NOT NULL,
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS custom_field_definitions (
                id UUID PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                field_type VARCHAR(50) NOT NULL,
                validation_rules TEXT NOT NULL DEFAULT '{}',
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS custom_field_values (
                member_id UUID NOT NULL REFERENCES members(id) ON DELETE CASCADE,
                field_id UUID NOT NULL REFERENCES custom_field_definitions(id) ON DELETE CASCADE,
                value TEXT NOT NULL,
                PRIMARY KEY (member_id, field_id)
            )
        """)

    conn.commit()
