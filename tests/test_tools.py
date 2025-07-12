import unittest
import os
from unittest.mock import patch, MagicMock
import sys

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tools.weather_tool import get_weather
from app.tools.math_tool import calculate_math


class TestWeatherTool(unittest.TestCase):
    """Test cases for the weather tool"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Set environment variable for testing
        os.environ["OPENWEATHER_API_KEY"] = "test-api-key"
    
    def tearDown(self):
        """Clean up after tests"""
        if "OPENWEATHER_API_KEY" in os.environ:
            del os.environ["OPENWEATHER_API_KEY"]
    
    @patch('app.tools.weather_tool.requests.get')
    def test_get_weather_success(self, mock_get):
        """Test successful weather API call"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "main": {"temp": 25.5, "humidity": 60},
            "weather": [{"description": "clear sky"}],
            "wind": {"speed": 3.5}
        }
        mock_get.return_value = mock_response
        
        result = get_weather.invoke({"location": "Paris"})
        
        # Check that the result contains expected information
        self.assertIn("Paris", result)
        self.assertIn("25.5°C", result)
        self.assertIn("clear sky", result)
        self.assertIn("60%", result)
        self.assertIn("3.5 m/s", result)
        
        # Verify API was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn("Paris", call_args[0][0])  # URL contains Paris
        self.assertIn("appid=test-api-key", call_args[0][0])  # API key in URL
    
    @patch('app.tools.weather_tool.requests.get')
    def test_get_weather_api_error(self, mock_get):
        """Test weather API error handling"""
        # Mock API error response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "city not found"}
        mock_get.return_value = mock_response
        
        result = get_weather.invoke({"location": "InvalidCity"})
        
        # Check that error is handled gracefully
        self.assertIn("Error", result)
        self.assertIn("city not found", result)
    
    @patch('app.tools.weather_tool.requests.get')
    def test_get_weather_network_error(self, mock_get):
        """Test weather tool with network error"""
        # Mock network error
        mock_get.side_effect = Exception("Network error")
        
        result = get_weather.invoke({"location": "Paris"})
        
        # Check that network error is handled gracefully
        self.assertIn("Error", result)
        self.assertIn("Network error", result)
    
    def test_get_weather_missing_api_key(self):
        """Test weather tool without API key"""
        # Remove API key
        if "OPENWEATHER_API_KEY" in os.environ:
            del os.environ["OPENWEATHER_API_KEY"]
        
        result = get_weather.invoke({"location": "Paris"})
        
        # Check that missing API key is handled
        self.assertIn("API key", result)
        self.assertIn("not configured", result)
    
    def test_get_weather_empty_location(self):
        """Test weather tool with empty location"""
        result = get_weather.invoke({"location": ""})
        
        # Check that empty location is handled
        self.assertIn("Error", result)
        self.assertIn("location", result)
    
    def test_get_weather_missing_location(self):
        """Test weather tool with missing location parameter"""
        result = get_weather.invoke({})
        
        # Check that missing location is handled
        self.assertIn("Error", result)
        self.assertIn("location", result)
    
    @patch('app.tools.weather_tool.requests.get')
    def test_get_weather_malformed_response(self, mock_get):
        """Test weather tool with malformed API response"""
        # Mock malformed response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"unexpected": "format"}
        mock_get.return_value = mock_response
        
        result = get_weather.invoke({"location": "Paris"})
        
        # Check that malformed response is handled
        self.assertIn("Error", result)


class TestMathTool(unittest.TestCase):
    """Test cases for the math tool"""
    
    def test_calculate_math_basic_operations(self):
        """Test basic mathematical operations"""
        test_cases = [
            ("2 + 2", "4"),
            ("10 - 5", "5"),
            ("3 * 4", "12"),
            ("8 / 2", "4"),
            ("2 ** 3", "8"),  # Exponentiation
            ("10 % 3", "1"),  # Modulo
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = calculate_math.invoke({"expression": expression})
                self.assertEqual(result, expected)
    
    def test_calculate_math_complex_expressions(self):
        """Test complex mathematical expressions"""
        test_cases = [
            ("(2 + 3) * 4", "20"),
            ("2 * (3 + 4)", "14"),
            ("10 / (2 + 3)", "2"),
            ("2 ** (3 + 1)", "16"),
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = calculate_math.invoke({"expression": expression})
                self.assertEqual(result, expected)
    
    def test_calculate_math_floating_point(self):
        """Test floating point calculations"""
        test_cases = [
            ("2.5 + 1.5", "4.0"),
            ("10.0 / 3.0", "3.3333333333333335"),
            ("3.14 * 2", "6.28"),
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = calculate_math.invoke({"expression": expression})
                self.assertEqual(result, expected)
    
    def test_calculate_math_invalid_expression(self):
        """Test math tool with invalid expressions"""
        invalid_expressions = [
            "2 +",  # Incomplete expression
            "2 / 0",  # Division by zero
            "invalid",  # Not a mathematical expression
            "2 + + 3",  # Invalid syntax
            "",  # Empty expression
        ]
        
        for expression in invalid_expressions:
            with self.subTest(expression=expression):
                result = calculate_math.invoke({"expression": expression})
                self.assertIn("Error", result)
    
    def test_calculate_math_missing_expression(self):
        """Test math tool with missing expression parameter"""
        result = calculate_math.invoke({})
        
        # Check that missing expression is handled
        self.assertIn("Error", result)
        self.assertIn("expression", result)
    
    def test_calculate_math_security_eval(self):
        """Test that math tool prevents dangerous eval operations"""
        dangerous_expressions = [
            "__import__('os').system('ls')",  # System command
            "exec('print(1)')",  # Code execution
            "eval('2+2')",  # Nested eval
            "open('/etc/passwd')",  # File access
        ]
        
        for expression in dangerous_expressions:
            with self.subTest(expression=expression):
                result = calculate_math.invoke({"expression": expression})
                # Should either return error or safe result, not execute dangerous code
                self.assertIsInstance(result, str)
                # The result should not contain system information
                self.assertNotIn("/etc/passwd", result)
                self.assertNotIn("root:", result)
    
    def test_calculate_math_large_numbers(self):
        """Test math tool with large numbers"""
        test_cases = [
            ("999999999999999999999999999999", "999999999999999999999999999999"),
            ("1000000000000000000000000000000 + 1", "1000000000000000000000000000001"),
            ("2 ** 100", str(2**100)),
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = calculate_math.invoke({"expression": expression})
                self.assertEqual(result, expected)
    
    def test_calculate_math_negative_numbers(self):
        """Test math tool with negative numbers"""
        test_cases = [
            ("-5 + 3", "-2"),
            ("10 + (-5)", "5"),
            ("-10 / -2", "5"),
            ("(-3) ** 2", "9"),
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = calculate_math.invoke({"expression": expression})
                self.assertEqual(result, expected)


class TestToolsIntegration(unittest.TestCase):
    """Integration tests for tools"""
    
    def setUp(self):
        """Set up test fixtures"""
        os.environ["OPENWEATHER_API_KEY"] = "test-api-key"
    
    def tearDown(self):
        """Clean up after tests"""
        if "OPENWEATHER_API_KEY" in os.environ:
            del os.environ["OPENWEATHER_API_KEY"]
    
    def test_tools_import_correctly(self):
        """Test that tools can be imported correctly"""
        from app.tools import get_weather, calculate_math
        
        # Check that tools are callable
        self.assertTrue(callable(get_weather))
        self.assertTrue(callable(calculate_math))
        
        # Check that tools have the expected attributes
        self.assertTrue(hasattr(get_weather, 'invoke'))
        self.assertTrue(hasattr(calculate_math, 'invoke'))
        
        # Check that tools have names
        self.assertEqual(get_weather.name, "get_weather")
        self.assertEqual(calculate_math.name, "calculate_math")
    
    def test_tools_have_descriptions(self):
        """Test that tools have proper descriptions"""
        from app.tools import get_weather, calculate_math
        
        # Check that tools have descriptions
        self.assertTrue(hasattr(get_weather, 'description'))
        self.assertTrue(hasattr(calculate_math, 'description'))
        
        # Check that descriptions are not empty
        self.assertIsNotNone(get_weather.description)
        self.assertIsNotNone(calculate_math.description)
        self.assertTrue(len(get_weather.description) > 0)
        self.assertTrue(len(calculate_math.description) > 0)


if __name__ == '__main__':
    unittest.main() 