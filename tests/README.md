# Tests

This directory contains unit tests for the FastAPI application.

## Structure

- `conftest.py` - Pytest fixtures and configuration
- `fixtures.py` - Test data fixtures
- `test_repositories.py` - Tests for repository layer
- `test_services.py` - Tests for service layer
- `test_user_service.py` - Tests for user service
- `test_api.py` - Tests for API endpoints
- `test_deps.py` - Tests for dependencies
- `test_models.py` - Tests for database models

## Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run specific test file
poetry run pytest tests/test_api.py -v

# Run specific test
poetry run pytest tests/test_api.py::TestAuthAPI::test_login_success -v
```

## Test Coverage

Tests cover:
- User repository operations (CRUD)
- Authentication services (password hashing, JWT tokens)
- User services
- API endpoints (auth, users, health)
- Dependencies and middleware
- Database models

## Fixtures

- `test_settings` - Test configuration
- `test_engine` - In-memory SQLite database
- `db_session` - Database session for tests
- `mock_user` - Mock user object
- `user_create_data` - User creation data
- `mock_db_session` - Mocked database session