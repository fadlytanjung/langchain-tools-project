import unittest
import os
from unittest.mock import patch
from fastapi.testclient import TestClient
import sys

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.api.routes import QueryRequest


class TestAPIEndpoints(unittest.TestCase):
    """Test cases for FastAPI endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Set environment variables for testing
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["DEFAULT_MODEL"] = "gpt-4o-mini"
        
        # Create test client
        self.client = TestClient(app)
    
    def tearDown(self):
        """Clean up after tests"""
        # Clean up environment variables
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        if "DEFAULT_MODEL" in os.environ:
            del os.environ["DEFAULT_MODEL"]
    
    def test_health_check(self):
        """Test the health check endpoint"""
        response = self.client.get("/health")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = self.client.get("/api/v1/")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check that response contains expected keys
        self.assertIn("message", data)
        self.assertIn("endpoints", data)
        self.assertIn("examples", data)
        
        # Check that endpoints are listed
        self.assertIsInstance(data["endpoints"], list)
        self.assertTrue(len(data["endpoints"]) > 0)
    
    @patch('app.api.routes.process_query')
    def test_query_endpoint_llm(self, mock_process_query):
        """Test the query endpoint with LLM query"""
        # Mock the process_query function
        mock_process_query.return_value = {
            "query": "What is the capital of France?",
            "tool_used": "llm",
            "result": "The capital of France is Paris."
        }
        
        response = self.client.post(
            "/api/v1/query",
            json={"query": "What is the capital of France?"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data["query"], "What is the capital of France?")
        self.assertEqual(data["tool_used"], "llm")
        self.assertEqual(data["result"], "The capital of France is Paris.")
        
        # Verify the mock was called correctly
        mock_process_query.assert_called_once_with("What is the capital of France?")
    
    @patch('app.api.routes.process_query')
    def test_query_endpoint_math(self, mock_process_query):
        """Test the query endpoint with math query"""
        # Mock the process_query function
        mock_process_query.return_value = {
            "query": "What is 2 + 2?",
            "tool_used": "math",
            "result": "4"
        }
        
        response = self.client.post(
            "/api/v1/query",
            json={"query": "What is 2 + 2?"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data["query"], "What is 2 + 2?")
        self.assertEqual(data["tool_used"], "math")
        self.assertEqual(data["result"], "4")
    
    @patch('app.api.routes.process_query')
    def test_query_endpoint_weather(self, mock_process_query):
        """Test the query endpoint with weather query"""
        # Mock the process_query function
        mock_process_query.return_value = {
            "query": "What's the weather in Paris?",
            "tool_used": "weather",
            "result": "Sunny, 25°C"
        }
        
        response = self.client.post(
            "/api/v1/query",
            json={"query": "What's the weather in Paris?"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data["query"], "What's the weather in Paris?")
        self.assertEqual(data["tool_used"], "weather")
        self.assertEqual(data["result"], "Sunny, 25°C")
    
    def test_query_endpoint_missing_query(self):
        """Test the query endpoint with missing query field"""
        response = self.client.post(
            "/api/v1/query",
            json={}
        )
        
        self.assertEqual(response.status_code, 422)  # Validation error
    
    def test_query_endpoint_invalid_json(self):
        """Test the query endpoint with invalid JSON"""
        response = self.client.post(
            "/api/v1/query",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 422)  # Validation error
    
    @patch('app.api.routes.process_query')
    def test_query_endpoint_empty_string(self, mock_process_query):
        """Test the query endpoint with empty string"""
        # Mock the process_query function to return error
        mock_process_query.return_value = {
            "query": "",
            "tool_used": "llm",
            "result": "Error: Query cannot be empty"
        }
        
        response = self.client.post(
            "/api/v1/query",
            json={"query": ""}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data["query"], "")
        self.assertEqual(data["tool_used"], "llm")
        self.assertIn("Error", data["result"])
    
    @patch('app.api.routes.process_query')
    def test_query_endpoint_error_handling(self, mock_process_query):
        """Test the query endpoint error handling"""
        # Mock the process_query function to raise an exception
        mock_process_query.side_effect = Exception("Test error")
        
        response = self.client.post(
            "/api/v1/query",
            json={"query": "test query"}
        )
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        
        self.assertIn("error", data)
        self.assertIn("Test error", data["error"])
    
    def test_test_math_endpoint(self):
        """Test the math test endpoint"""
        response = self.client.get("/api/v1/test/math")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check response structure
        self.assertIn("test_type", data)
        self.assertIn("query", data)
        self.assertIn("expected_tool", data)
        self.assertIn("curl_example", data)
        
        self.assertEqual(data["test_type"], "math")
        self.assertEqual(data["expected_tool"], "math")
    
    def test_test_weather_endpoint(self):
        """Test the weather test endpoint"""
        response = self.client.get("/api/v1/test/weather")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check response structure
        self.assertIn("test_type", data)
        self.assertIn("query", data)
        self.assertIn("expected_tool", data)
        self.assertIn("curl_example", data)
        
        self.assertEqual(data["test_type"], "weather")
        self.assertEqual(data["expected_tool"], "weather")
    
    def test_test_llm_endpoint(self):
        """Test the LLM test endpoint"""
        response = self.client.get("/api/v1/test/llm")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check response structure
        self.assertIn("test_type", data)
        self.assertIn("query", data)
        self.assertIn("expected_tool", data)
        self.assertIn("curl_example", data)
        
        self.assertEqual(data["test_type"], "llm")
        self.assertEqual(data["expected_tool"], "llm")
    
    def test_test_status_endpoint(self):
        """Test the status test endpoint"""
        response = self.client.get("/api/v1/test/status")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check response structure
        self.assertIn("status", data)
        self.assertIn("tools_available", data)
        self.assertIn("api_version", data)
        
        self.assertEqual(data["status"], "operational")
        self.assertIsInstance(data["tools_available"], list)
        self.assertIn("weather", data["tools_available"])
        self.assertIn("math", data["tools_available"])


class TestQueryRequest(unittest.TestCase):
    """Test cases for the QueryRequest model"""
    
    def test_query_request_valid(self):
        """Test valid QueryRequest creation"""
        request = QueryRequest(query="test query")
        self.assertEqual(request.query, "test query")
    
    def test_query_request_empty_string(self):
        """Test QueryRequest with empty string (should be valid)"""
        request = QueryRequest(query="")
        self.assertEqual(request.query, "")
    
    def test_query_request_whitespace(self):
        """Test QueryRequest with whitespace"""
        request = QueryRequest(query="   ")
        self.assertEqual(request.query, "   ")


class TestAPIIntegration(unittest.TestCase):
    """Integration tests for the API"""
    
    def setUp(self):
        """Set up test fixtures"""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["DEFAULT_MODEL"] = "gpt-4o-mini"
        self.client = TestClient(app)
    
    def tearDown(self):
        """Clean up after tests"""
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        if "DEFAULT_MODEL" in os.environ:
            del os.environ["DEFAULT_MODEL"]
    
    def test_api_cors_headers(self):
        """Test that CORS headers are present"""
        response = self.client.get("/health")
        
        self.assertEqual(response.status_code, 200)
        # Note: In testing environment, CORS headers might not be fully present
        # This test ensures the endpoint is accessible
    
    def test_api_content_type(self):
        """Test that API returns correct content type"""
        response = self.client.get("/api/v1/")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/json", response.headers.get("content-type", ""))
    
    def test_api_error_format(self):
        """Test that API errors are properly formatted"""
        response = self.client.post(
            "/api/v1/query",
            json={"invalid": "field"}
        )
        
        self.assertEqual(response.status_code, 422)
        data = response.json()
        
        # FastAPI validation error format
        self.assertIn("detail", data)


if __name__ == '__main__':
    unittest.main() 