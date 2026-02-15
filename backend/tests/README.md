# Unit Tests

## Running Tests

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run tests for a specific module
pytest tests/test_visor_service.py

# Run specific test class
pytest tests/test_visor_service.py::TestVisorServiceCreate

# Run specific test
pytest tests/test_visor_service.py::TestVisorServiceCreate::test_create_visor_with_all_fields

# Run tests with coverage
pytest --cov=app tests/
```

## Test Database

Tests use SQLite in-memory database (`sqlite:///:memory:`) configured in `conftest.py` for fast, isolated test execution. Each test gets a clean database automatically.
