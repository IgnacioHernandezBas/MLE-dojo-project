# Tests

Unit tests and integration tests for the agent package.

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run specific test file
```bash
pytest tests/test_agent.py
```

### Run with verbose output
```bash
pytest tests/ -v
```

### Run with coverage
```bash
pytest tests/ --cov=agent --cov-report=html
```

## Test Organization

- **test_agent.py** - Core agent functionality tests
- **test_wrappers.py** - Wrapper tests (to be added)
- **test_training.py** - Training pipeline tests (to be added)
- **test_integration.py** - End-to-end integration tests (to be added)

## Adding New Tests

When adding new functionality:

1. Create corresponding test file in `tests/`
2. Follow the naming convention `test_<module>.py`
3. Use descriptive test function names: `test_<functionality>`
4. Include docstrings explaining what each test validates
5. Use fixtures for common setup/teardown

## Test Coverage Goals

- Aim for >80% code coverage
- All core functionality should have tests
- Edge cases and error handling should be tested
- Integration tests for complete workflows

## CI/CD

Tests should be run automatically in CI/CD pipeline before:
- Merging pull requests
- Creating releases
- Deploying to production
