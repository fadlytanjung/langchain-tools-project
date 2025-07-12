"""
Test configuration for pytest
"""
import os
import sys
import pytest

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables"""
    # Set test environment variables
    os.environ["OPENAI_API_KEY"] = "test-api-key"
    os.environ["DEFAULT_MODEL"] = "gpt-4o-mini"
    os.environ["OPENWEATHER_API_KEY"] = "test-weather-key"
    
    yield
    
    # Clean up after tests
    test_env_vars = [
        "OPENAI_API_KEY",
        "DEFAULT_MODEL", 
        "OPENWEATHER_API_KEY"
    ]
    
    for var in test_env_vars:
        if var in os.environ:
            del os.environ[var] 