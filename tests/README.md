# Chat Application Tests

This directory contains unit tests for the chat application components.

## Test Files

### `test_qb_model_output_parser.py`
Comprehensive unit tests for the `QBModelOutputParser` class, which handles parsing and processing of QuickBooks model outputs.

**Test Coverage:**
- Initialization and constructor behavior
- Success and error state management
- Tool call processing and integration
- Output formatting and validation
- Edge cases and error handling
- Method chaining and interface compliance

**Key Test Categories:**
1. **Initialization Tests**: Verify proper setup with and without tool call runners
2. **Success State Tests**: Test handling of successful responses with various content types
3. **Tool Call Tests**: Test processing of tool calls and integration with tool call runners
4. **Error Handling Tests**: Test various error scenarios and error state management
5. **Output Validation Tests**: Verify correct output format and success/failure logic
6. **Edge Case Tests**: Test boundary conditions and unusual input scenarios

## Running Tests

### Run All Tests
```bash
python3 tests/run_tests.py
```

### Run Specific Test File
```bash
python3 -m unittest tests.test_qb_model_output_parser -v
```

### Run Individual Test Method
```bash
python3 -m unittest tests.test_qb_model_output_parser.TestQBModelOutputParser.test_init -v
```

## Test Dependencies

The tests use the following mocking and testing utilities:
- `unittest` - Python's built-in testing framework
- `unittest.mock` - For mocking dependencies and external components
- Custom mock implementations of `IToolCallRunner` and related interfaces

## Test Structure

Each test class follows the standard unittest pattern:
- `setUp()` - Initialize test fixtures and mocks
- Individual test methods for specific functionality
- Proper assertions and error checking
- Clean separation of concerns

## Adding New Tests

When adding new tests:
1. Follow the existing naming convention: `test_<method_name>_<scenario>`
2. Use descriptive test method names that explain what is being tested
3. Include proper docstrings explaining the test purpose
4. Use appropriate assertions and error messages
5. Ensure tests are independent and can run in any order 