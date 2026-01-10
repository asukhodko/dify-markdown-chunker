# Testing Documentation

This document describes the testing strategy and structure for this project after the test suite cleanup.

## Test Suite Overview

The test suite has been cleaned up and optimized to work with the migration adapter architecture:

- **Total tests removed**: 0
- **Total tests adapted**: 45
- **Migration-compatible tests**: Tests that work without modification

## Test Categories

### Migration Tests (`test_migration_*.py`)
Tests that use the `MigrationAdapter` to bridge legacy functionality with the new Chunkana library.

### Integration Tests (`test_integration_*.py`)
Tests that verify component interactions and end-to-end functionality.

### Adapted Tests (`test_*_adapted.py`)
Legacy tests that have been adapted to work with the new architecture while preserving their original test logic.

## Running Tests

### All Tests
```bash
make test-all
```

### Migration-Compatible Tests Only
```bash
make test
```

### Specific Test Categories
```bash
# Migration tests
pytest tests/test_migration_*.py -v

# Integration tests  
pytest tests/test_integration_*.py -v

# Adapted tests
pytest tests/test_*_adapted.py -v
```

### Test Coverage
```bash
make test-coverage
```

## Test Development Guidelines

1. **New tests should use MigrationAdapter**: Don't import legacy modules directly
2. **Follow naming conventions**: Use appropriate prefixes for test categories
3. **Preserve test intent**: When adapting tests, maintain the original test logic
4. **Add property tests**: Use Hypothesis for testing universal properties
5. **Test error conditions**: Ensure error handling is properly tested

## Test Infrastructure

- **pytest.ini**: Configuration for test discovery and execution
- **Makefile**: Test targets for different test categories
- **Migration adapter**: Bridge between legacy and new implementations

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure you're using `MigrationAdapter` instead of legacy imports
2. **Test discovery**: Check that test files follow naming conventions
3. **Assertion failures**: Verify that adapted tests preserve original assertions

### Getting Help

If you encounter issues with tests:
1. Check the test logs for specific error messages
2. Verify that the migration adapter is working correctly
3. Review the test adaptation documentation
4. Run tests in verbose mode for more details

## Test Cleanup History

This test suite was cleaned up on 2026-01-10 with the following changes:
- Removed redundant tests that duplicated existing coverage
- Adapted valuable legacy tests to use the migration adapter
- Updated test infrastructure for better organization
- Preserved unique test logic and assertions

For more details, see the cleanup reports in the project documentation.
