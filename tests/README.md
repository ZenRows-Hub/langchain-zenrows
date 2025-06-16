# Testing Guide for langchain-zenrows

This directory contains comprehensive tests for the langchain-zenrows package.

## Test Structure

```
tests/
├── conftest.py                 # Pytest configuration and shared fixtures
├── unit_tests/                 # Unit tests (no API calls)
│   ├── __init__.py
│   └── test_zenrows_universal_scraper.py
├── integration_tests/          # Integration tests (real API calls)
│   ├── __init__.py
│   └── test_zenrows_universal_scraper.py
└── README.md                   # This file
```

## Quick Start

### 1. Install Test Dependencies

```bash
pip install -e .[test]
```

### 2. Run Tests

```bash
# Run all tests (recommended)
python run_tests.py

# Or use pytest directly
pytest
```

## Test Categories

### Unit Tests
- **Location**: `tests/unit_tests/`
- **Purpose**: Test code logic without making API calls
- **Requirements**: None (no API key needed)
- **Coverage**: Input validation, error handling, parameter preparation

**Run unit tests only:**
```bash
python run_tests.py --unit-only
# or
pytest tests/unit_tests/
```

### Integration Tests
- **Location**: `tests/integration_tests/`
- **Purpose**: Test real API functionality
- **Requirements**: `ZENROWS_API_KEY` environment variable
- **Coverage**: End-to-end functionality, real API responses

**Run integration tests only:**
```bash
export ZENROWS_API_KEY="<ZENROWS_API_KEY>"
# or
set ZENROWS_API_KEY=<ZENROWS_API_KEY>

python run_tests.py --integration-only
# or
pytest -m integration
```


## Test Commands Reference

### Using run_tests.py (Recommended)

```bash
# Basic usage
python run_tests.py                    # Run all tests
python run_tests.py --unit-only        # Unit tests only
python run_tests.py --integration-only # Integration tests only
python run_tests.py --verbose         # Verbose output
```

### Using pytest directly

```bash
# Basic pytest commands
pytest                                 # Run all tests
pytest -v                             # Verbose output
pytest tests/unit_tests/              # Unit tests only
pytest tests/integration_tests/       # Integration tests only

# Specific test files
pytest tests/unit_tests/test_zenrows_universal_scraper.py
pytest tests/integration_tests/test_zenrows_universal_scraper.py::TestZenRowsUniversalScraperIntegration::test_basic_scraping
```

## Environment Variables

### Required for Integration Tests
- `ZENROWS_API_KEY`: Your ZenRows API key

### Optional
- `PYTEST_CURRENT_TEST`: Set automatically by pytest

## Test Data and Fixtures

The tests use several test URLs and fixtures:

### Test URLs (defined in conftest.py)
- `https://httpbin.io/html` - Basic HTML page
- `https://httpbin.io/json` - JSON response
- `https://httpbin.io/ip` - IP information
- `https://httpbin.io/headers` - Header inspection
- `https://www.scrapingcourse.com/javascript-rendering` - JavaScript-heavy page

### Shared Fixtures
- `zenrows_api_key`: Provides API key for tests
- `mock_response`: Mock HTTP response for unit tests
- `sample_html`: Sample HTML content
- `sample_css_extractor`: Sample CSS extractor configuration
- `test_urls`: Dictionary of test URLs