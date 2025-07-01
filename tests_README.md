# Roster Optimizer Test Suite

This directory contains comprehensive unit and integration tests for the MLB and F1 daily fantasy lineup optimizers.

## Test Structure

The tests are organized as follows:

```
roster_opt/
│
├── run_tests.py         # Main test runner script
├── run_tests.bat        # Windows batch script to run tests
│
├── MLB_Optimizer/
│   └── tests/
│       ├── __init__.py
│       ├── test_optimizer.py           # Basic MLB optimizer tests
│       ├── test_advanced_optimizer.py  # Advanced MLB optimizer tests
│       ├── test_injury_manager.py      # Injury manager tests
│       └── test_integration.py         # MLB integration tests
│
├── F1_Optimizer/
│   └── tests/
│       ├── __init__.py
│       ├── test_optimizer.py           # Basic F1 optimizer tests
│       ├── test_advanced_optimizer.py  # Advanced F1 optimizer tests
│       └── test_integration.py         # F1 integration tests
│
└── WNBA_Optimizer/
    └── tests/
        ├── __init__.py
        ├── test_optimizer.py           # Basic WNBA Showdown optimizer tests
        ├── test_advanced_optimizer.py  # Advanced WNBA Showdown optimizer tests
        └── test_integration.py         # WNBA integration tests
```

## Running Tests

### All Tests

To run all tests for both optimizers:

```
python run_tests.py
```

Or use the batch file:

```
run_tests.bat
```

### Specific Optimizer Tests

To run tests for only the MLB optimizer:

```
python run_tests.py --optimizer mlb
```

Or:

```
run_tests.bat mlb
```

To run tests for only the F1 optimizer:

```
python run_tests.py --optimizer f1
```

Or:

```
run_tests.bat f1
```

## Test Coverage

The test suite covers:

### Unit Tests
- Data loading and validation
- Roster position requirements
- Salary cap constraints
- Team stacking functionality
- Player appearance limitations
- Injured player filtering
- Captain point calculation (F1)

### Integration Tests
- End-to-end optimization workflow
- Multiple lineup generation
- Lineup diversity enforcement
- Output file generation
- Consistency between basic and advanced optimizers

## Adding New Tests

When adding new functionality to the optimizers, add corresponding tests to maintain good test coverage. Place unit tests in the appropriate test file and integration tests in the `test_integration.py` files.
