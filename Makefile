# Load local overrides (DB_PASSWORD etc.) if a .env file is present
-include .env
export

COMPOSE_DEV = docker compose -f docker-compose.dev.yml
TEST_DB_NAME = membermocker_test

# Tests always run against a dedicated test database so they never wipe real data
TEST_ENV = DB_HOST=127.0.0.1 DB_PORT=5432 DB_NAME=$(TEST_DB_NAME)

.PHONY: pytest pytest-including-slow db-up db-down test-db

## Run the fast test suite (external APIs mocked, requires Docker for PostgreSQL)
pytest: test-db
	cd backend && $(TEST_ENV) uv run pytest test_api.py

## Run the full test suite including slow tests that hit Ollama and OpenStreetMap
pytest-including-slow: test-db
	cd backend && $(TEST_ENV) uv run pytest test_api.py --run-expensive

## Start the PostgreSQL container and wait until it is healthy
db-up:
	$(COMPOSE_DEV) up -d --wait postgres

## Stop the PostgreSQL container
db-down:
	$(COMPOSE_DEV) stop postgres

## Ensure the test database exists
test-db: db-up
	$(COMPOSE_DEV) exec postgres psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '$(TEST_DB_NAME)'" | grep -q 1 || \
		$(COMPOSE_DEV) exec postgres psql -U postgres -c "CREATE DATABASE $(TEST_DB_NAME)"
