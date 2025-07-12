import unittest
import os
import sys

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestBasicImports(unittest.TestCase):
    """Basic tests to ensure imports work correctly"""
    
    def setUp(self):
        """Set up test environment"""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["DEFAULT_MODEL"] = "gpt-4o-mini"
        os.environ["OPENWEATHER_API_KEY"] = "test-weather-key"
    
    def tearDown(self):
        """Clean up after tests"""
        test_env_vars = ["OPENAI_API_KEY", "DEFAULT_MODEL", "OPENWEATHER_API_KEY"]
        for var in test_env_vars:
            if var in os.environ:
                del os.environ[var]
    
    def test_import_tools(self):
        """Test that tools can be imported"""
        from app.tools import get_weather, calculate_math
        
        # Check that tools are callable
        self.assertTrue(callable(get_weather))
        self.assertTrue(callable(calculate_math))
        
        # Check that tools have names
        self.assertEqual(get_weather.name, "get_weather")
        self.assertEqual(calculate_math.name, "calculate_math")
    
    def test_import_agent(self):
        """Test that agent can be imported"""
        from app.core.agent import LangGraphAgent, AgentState
        
        # Check that classes exist
        self.assertTrue(LangGraphAgent)
        self.assertTrue(AgentState)
    
    def test_import_api(self):
        """Test that API components can be imported"""
        from app.main import app
        from app.api.routes import QueryRequest
        
        # Check that components exist
        self.assertIsNotNone(app)
        self.assertTrue(QueryRequest)
    
    def test_config_import(self):
        """Test that config can be imported"""
        from app.core.config import settings
        
        # Check that settings exist
        self.assertIsNotNone(settings)
        self.assertTrue(hasattr(settings, 'OPENAI_API_KEY'))
        self.assertTrue(hasattr(settings, 'DEFAULT_MODEL'))


class TestMathTool(unittest.TestCase):
    """Test the math tool functionality"""
    
    def setUp(self):
        """Set up test environment"""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["DEFAULT_MODEL"] = "gpt-4o-mini"
    
    def tearDown(self):
        """Clean up after tests"""
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        if "DEFAULT_MODEL" in os.environ:
            del os.environ["DEFAULT_MODEL"]
    
    def test_basic_math_operations(self):
        """Test basic math operations"""
        from app.tools.math_tool import calculate_math
        
        # Test simple addition
        result = calculate_math.invoke({"expression": "2 + 2"})
        self.assertIn("4", result)  # Could be "4" or "4.0"
        
        # Test multiplication
        result = calculate_math.invoke({"expression": "3 * 4"})
        self.assertIn("12", result)
        
        # Test division
        result = calculate_math.invoke({"expression": "10 / 2"})
        self.assertIn("5", result)


class TestHealthCheck(unittest.TestCase):
    """Test basic API health check"""
    
    def setUp(self):
        """Set up test environment"""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["DEFAULT_MODEL"] = "gpt-4o-mini"
    
    def tearDown(self):
        """Clean up after tests"""
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        if "DEFAULT_MODEL" in os.environ:
            del os.environ["DEFAULT_MODEL"]
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})


if __name__ == '__main__':
    unittest.main() 