# Property Finder Test Suite

Comprehensive testing suite for the Property Finder application.

## Test Categories

### 1. Data Processing Tests (`test_data_processing.py`)
- Document processing validation
- Data structure validation
- Customer profile structure tests
- Recommendation data structure tests
- Column and data type validation

### 2. Service Layer Tests (`test_services.py`)
- OpenAI service integration tests
- API key validation
- Recommendation engine logic
- Filtering and sorting tests
- Session state management

### 3. UI Component Tests (`test_ui_components.py`)
- Property card component tests
- Metric display formatting
- Suburb comparison functionality
- Chart data preparation
- Form validation

## Running Tests

### From Command Line

Run all tests:
```bash
pytest
```

Run specific test file:
```bash
pytest tests/test_data_processing.py
```

Run with verbose output:
```bash
pytest -v
```

Run tests matching a pattern:
```bash
pytest -k "test_validation"
```

### From Frontend UI

1. Navigate to **System Tests** in the sidebar
2. Select the test suite you want to run
3. Click **"▶️ Run Tests"**
4. View results in real-time

## Test Suite Features

### Quick Tests Tab
- Select and run specific test suites
- View execution progress
- See pass/fail summary
- Access detailed test output

### Test Results Tab
- View historical test runs
- Compare results across runs
- Track test performance over time

### Data Validation Tab
- Validate customer profile data
- Check suburb data integrity
- Verify recommendations structure
- Real-time validation of session data

### System Health Tab
- Check installed dependencies
- Verify API configuration
- Validate file system structure
- Monitor system status

## Writing New Tests

### Test Structure
```python
class TestFeatureName:
    """Test description"""

    def test_specific_functionality(self):
        """Test case description"""
        # Arrange
        sample_data = create_test_data()

        # Act
        result = function_to_test(sample_data)

        # Assert
        assert result == expected_value
```

### Best Practices
1. Use descriptive test names
2. Test one thing per test function
3. Include docstrings
4. Use fixtures for common setup
5. Keep tests independent
6. Mock external dependencies

## Test Coverage

Current coverage areas:
- ✅ Data validation
- ✅ Service layer logic
- ✅ UI component rendering
- ✅ Form validation
- ✅ Session management
- ⏳ End-to-end workflows (planned)
- ⏳ Performance tests (planned)

## Continuous Testing

### Regular Testing Schedule
- **Before deployment**: Run full test suite
- **After data updates**: Run data validation
- **Weekly**: Run all tests to catch regressions
- **After feature changes**: Run relevant test suite

### Automated Testing
Tests can be integrated into CI/CD pipelines:
```bash
# Example GitHub Actions workflow
pytest --cov=app --cov-report=html
```

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure app directory is in Python path
export PYTHONPATH="${PYTHONPATH}:./app"
```

**Missing Dependencies**
```bash
pip install pytest pandas numpy
```

**Test Failures**
1. Check test output for specific failure
2. Verify test data matches expected format
3. Ensure session state is properly initialized
4. Check for recent code changes

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure tests pass before committing
3. Update this README if adding new test categories
4. Maintain minimum 80% code coverage

## Support

For test-related issues:
1. Check test output logs
2. Review data validation results
3. Check system health dashboard
4. Verify all dependencies are installed
