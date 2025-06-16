"""Pytest configuration and shared fixtures for langchain-zenrows tests."""

import os
import pytest


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (require API key)"
    )
    config.addinivalue_line("markers", "slow: marks tests as slow running tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add integration marker to all tests in integration_tests directory
        if "integration_tests" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Add slow marker to tests that are explicitly marked or contain 'slow' in name
        if "slow" in item.name or any(
            mark.name == "slow" for mark in item.iter_markers()
        ):
            item.add_marker(pytest.mark.slow)


@pytest.fixture(scope="session")
def zenrows_api_key():
    """Provide ZenRows API key for testing."""
    api_key = os.environ.get("ZENROWS_API_KEY")
    if not api_key:
        pytest.skip("ZENROWS_API_KEY environment variable not set")
    return api_key


@pytest.fixture(scope="session")
def has_zenrows_api_key():
    """Check if ZenRows API key is available."""
    return bool(os.environ.get("ZENROWS_API_KEY"))


@pytest.fixture
def mock_response():
    """Create a mock response object for testing."""
    from unittest.mock import Mock

    response = Mock()
    response.text = "<html><body>Mock content</body></html>"
    response.content = b"<html><body>Mock content</body></html>"
    return response


@pytest.fixture
def sample_html():
    """Provide sample HTML content for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
    </head>
    <body>
        <h1>Test Title</h1>
        <p>Test paragraph content.</p>
        <div class="content">
            <span>Test span content</span>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def sample_css_extractor():
    """Provide sample CSS extractor configuration."""
    import json

    return json.dumps({"title": "h1", "content": "p", "spans": "span"})


@pytest.fixture
def test_urls():
    """Provide test URLs for different scenarios."""
    return {
        "html": "https://httpbin.io/html",
        "json": "https://httpbin.io/json",
        "ip": "https://httpbin.io/ip",
        "headers": "https://httpbin.io/headers",
        "javascript": "https://www.scrapingcourse.com/javascript-rendering",
    }
