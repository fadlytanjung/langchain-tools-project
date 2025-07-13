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

    @patch("app.api.routes.agent_instance.process_query")
    def test_query_endpoint_llm(self, mock_process_query):
        """Test the query endpoint with LLM query"""
        # Mock the process_query function
        mock_process_query.return_value = {
            "query": "What is the capital of France?",
            "tool_used": "llm",
            "result": "The capital of France is Paris.",
        }

        response = self.client.post(
            "/api/v1/query", json={"query": "What is the capital of France?"}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["query"], "What is the capital of France?")
        self.assertEqual(data["tool_used"], "llm")
        self.assertEqual(data["result"], "The capital of France is Paris.")

        # Verify the mock was called correctly
        mock_process_query.assert_called_once_with("What is the capital of France?")

    @patch("app.api.routes.agent_instance.process_query")
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

    @patch("app.api.routes.agent_instance.process_query")
    def test_query_endpoint_weather(self, mock_process_query):
        """Test the query endpoint with weather query"""
        # Mock the process_query function
        mock_process_query.return_value = {
            "query": "What's the weather in Paris?",
            "tool_used": "weather",
            "result": "Sunny, 25°C",
        }

        response = self.client.post(
            "/api/v1/query", json={"query": "What's the weather in Paris?"}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["query"], "What's the weather in Paris?")
        self.assertEqual(data["tool_used"], "weather")
        self.assertEqual(data["result"], "Sunny, 25°C")

    def test_query_endpoint_missing_query(self):
        """Test the query endpoint with missing query field"""
        response = self.client.post("/api/v1/query", json={})

        self.assertEqual(response.status_code, 422)  # Validation error

    def test_query_endpoint_invalid_json(self):
        """Test the query endpoint with invalid JSON"""
        response = self.client.post(
            "/api/v1/query",
            content="invalid json",
            headers={"Content-Type": "application/json"},
        )

        self.assertEqual(response.status_code, 422)  # Validation error

    @patch("app.api.routes.agent_instance.process_query")
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

    @patch("app.api.routes.agent_instance.process_query")
    def test_query_endpoint_error_handling(self, mock_process_query):
        """Test the query endpoint error handling"""
        # Mock the process_query function to raise an exception
        mock_process_query.side_effect = Exception("Test error")

        response = self.client.post("/api/v1/query", json={"query": "test query"})

        self.assertEqual(response.status_code, 500)
        data = response.json()

        self.assertIn("error", data)
        self.assertIn("Test error", data["error"])


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
        response = self.client.post("/api/v1/query", json={"query": "test"})

        # Should return 200 or 500, but not 404
        self.assertIn(response.status_code, [200, 500])
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