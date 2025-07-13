import unittest
import asyncio
import os
from unittest.mock import patch, MagicMock, Mock
import sys

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.agent import LangGraphAgent, AgentState
from langchain_core.messages import HumanMessage, AIMessage


class TestLangGraphAgent(unittest.TestCase):
    """Test cases for LangGraph Agent"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Set environment variables for testing
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["DEFAULT_MODEL"] = "gpt-4o-mini"
        
    def tearDown(self):
        """Clean up after each test method."""
        # Clean up environment variables
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        if "DEFAULT_MODEL" in os.environ:
            del os.environ["DEFAULT_MODEL"]
    
    @patch('app.core.agent.ChatOpenAI')
    def test_agent_initialization(self, mock_chat_openai):
        """Test that the agent initializes correctly"""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        agent = LangGraphAgent()
        
        # Check that ChatOpenAI was called with correct parameters
        mock_chat_openai.assert_called_with(model="gpt-4o-mini", temperature=0)
        
        # Check that the agent has the required attributes
        self.assertIsNotNone(agent.llm)
        self.assertIsNotNone(agent.llm_with_tools)
        self.assertIsNotNone(agent.graph)
    
    @patch('app.core.agent.settings')
    def test_agent_initialization_missing_api_key(self, mock_settings):
        """Test that agent raises error when API key is missing"""
        mock_settings.OPENAI_API_KEY = None
        
        with self.assertRaises(ValueError) as context:
            LangGraphAgent()
        
        self.assertIn("OpenAI API key is required", str(context.exception))
    
    @patch('app.core.agent.settings')
    def test_agent_initialization_missing_model(self, mock_settings):
        """Test that agent raises error when model is missing"""
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.DEFAULT_MODEL = None
        
        with self.assertRaises(ValueError) as context:
            LangGraphAgent()
        
        self.assertIn("Default model must be specified", str(context.exception))
    
    @patch('app.core.agent.ChatOpenAI')
    def test_agent_state_structure(self, mock_chat_openai):
        """Test that AgentState has the correct structure"""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        # Test state creation
        state: AgentState = {}
        
        # Check that state can hold the expected keys
        state["messages"] = [HumanMessage(content="test")]
        state["tool_used"] = "llm"
        state["result"] = "test result"
        
        self.assertEqual(len(state["messages"]), 1)
        self.assertEqual(state["tool_used"], "llm")
        self.assertEqual(state["result"], "test result")
    
    @patch('app.core.agent.ChatOpenAI')
    def test_llm_call_router(self, mock_chat_openai):
        """Test the routing logic"""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "math"
        mock_llm.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm
        
        agent = LangGraphAgent()
        
        # Test routing for math query
        state: AgentState = {}
        state["messages"] = [HumanMessage(content="What is 2 + 2?")]
        
        result_state = agent.llm_call_router(state)
        
        self.assertEqual(result_state.get("tool_used"), "math")
    
    @patch('app.core.agent.ChatOpenAI')
    def test_llm_call_router_weather(self, mock_chat_openai):
        """Test routing for weather queries"""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "weather"
        mock_llm.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm
        
        agent = LangGraphAgent()
        
        # Test routing for weather query
        state: AgentState = {}
        state["messages"] = [HumanMessage(content="What's the weather in Paris?")]
        
        result_state = agent.llm_call_router(state)
        
        self.assertEqual(result_state.get("tool_used"), "weather")
    
    @patch('app.core.agent.ChatOpenAI')
    def test_llm_call_router_llm(self, mock_chat_openai):
        """Test routing for general LLM queries"""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "llm"
        mock_llm.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm
        
        agent = LangGraphAgent()
        
        # Test routing for general query
        state: AgentState = {}
        state["messages"] = [HumanMessage(content="What is the capital of France?")]
        
        result_state = agent.llm_call_router(state)
        
        self.assertEqual(result_state.get("tool_used"), "llm")
    
    @patch('app.core.agent.ChatOpenAI')
    def test_agent_node(self, mock_chat_openai):
        """Test the agent node for LLM queries"""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "The capital of France is Paris."
        mock_llm.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm
        
        agent = LangGraphAgent()
        
        # Test agent node
        state: AgentState = {}
        state["messages"] = [HumanMessage(content="What is the capital of France?")]
        
        result_state = agent.agent(state)
        
        self.assertEqual(result_state.get("tool_used"), "llm")
        self.assertEqual(result_state.get("result"), "The capital of France is Paris.")
    
    @patch('app.core.agent.ChatOpenAI')
    def test_agent_node_empty_messages(self, mock_chat_openai):
        """Test agent node with empty messages"""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        agent = LangGraphAgent()
        
        # Test with empty messages
        state: AgentState = {}
        state["messages"] = []
        
        result_state = agent.agent(state)
        
        self.assertEqual(result_state.get("tool_used"), "llm")
        self.assertEqual(result_state.get("result"), "No messages to process")
    
    @patch('app.core.agent.ChatOpenAI')
    def test_route_decision(self, mock_chat_openai):
        """Test the route decision logic"""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        agent = LangGraphAgent()
        
        # Test different routing decisions
        test_cases = [
            ("math", "math"),
            ("weather", "weather"),
            ("llm", "llm"),
            (None, "llm"),  # Default case
        ]
        
        for tool_used, expected_route in test_cases:
            state: AgentState = {}
            if tool_used is not None:
                state["tool_used"] = tool_used
            
            route = agent.route_decision(state)
            self.assertEqual(route, expected_route)
    
    @patch('app.core.agent.ChatOpenAI')
    @patch('app.core.agent.get_weather')
    def test_agent_with_tools_weather(self, mock_get_weather, mock_chat_openai):
        """Test agent with tools for weather queries"""
        mock_llm = MagicMock()
        
        # Create a proper mock AIMessage with tool_calls
        mock_response = Mock(spec=AIMessage)
        mock_response.content = "I'll get the weather for you"
        mock_response.tool_calls = [{"name": "get_weather", "args": {"location": "Paris"}, "id": "test_id"}]

        # Mock the bind_tools method to return a mock that returns our response
        mock_llm_with_tools = MagicMock()
        mock_llm_with_tools.invoke.return_value = mock_response
        mock_llm.bind_tools.return_value = mock_llm_with_tools

        mock_chat_openai.return_value = mock_llm
        mock_get_weather.invoke.return_value = "Sunny, 25°C"
        
        agent = LangGraphAgent()
        
        # Test weather tool execution
        state: AgentState = {}
        state["messages"] = [HumanMessage(content="What's the weather in Paris?")]
        
        result_state = agent.agent_with_tools(state)
        
        self.assertEqual(result_state.get("tool_used"), "weather")
        self.assertEqual(result_state.get("result"), "Sunny, 25°C")
        mock_get_weather.invoke.assert_called_once_with({"location": "Paris"})
    
    @patch('app.core.agent.ChatOpenAI')
    @patch('app.core.agent.calculate_math')
    def test_agent_with_tools_math(self, mock_calculate_math, mock_chat_openai):
        """Test agent with tools for math queries"""
        mock_llm = MagicMock()
        
        # Create a proper mock AIMessage with tool_calls
        mock_response = Mock(spec=AIMessage)
        mock_response.content = "I'll calculate that for you"
        mock_response.tool_calls = [{"name": "calculate_math", "args": {"expression": "2+2"}, "id": "test_id"}]

        # Mock the bind_tools method to return a mock that returns our response
        mock_llm_with_tools = MagicMock()
        mock_llm_with_tools.invoke.return_value = mock_response
        mock_llm.bind_tools.return_value = mock_llm_with_tools

        mock_chat_openai.return_value = mock_llm
        mock_calculate_math.invoke.return_value = "4"
        
        agent = LangGraphAgent()
        
        # Test math tool execution
        state: AgentState = {}
        state["messages"] = [HumanMessage(content="What is 2+2?")]
        
        result_state = agent.agent_with_tools(state)
        
        self.assertEqual(result_state.get("tool_used"), "math")
        self.assertEqual(result_state.get("result"), "4")
        mock_calculate_math.invoke.assert_called_once_with({"expression": "2+2"})


class TestAgentProcessQuery(unittest.TestCase):
    """Test cases for the process_query function"""
    
    def setUp(self):
        """Set up test fixtures"""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["DEFAULT_MODEL"] = "gpt-4o-mini"
    
    def tearDown(self):
        """Clean up after tests"""
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        if "DEFAULT_MODEL" in os.environ:
            del os.environ["DEFAULT_MODEL"]
    
    @patch('app.core.agent.ChatOpenAI')
    def test_process_query_empty_string(self, mock_chat_openai):
        """Test processing an empty query"""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        agent = LangGraphAgent()
        
        # Test with empty query
        result = asyncio.run(agent.process_query(""))
        
        self.assertEqual(result["query"], "")
        self.assertEqual(result["tool_used"], "llm")
        self.assertIn("Error: Query cannot be empty", result["result"])
    
    @patch('app.core.agent.ChatOpenAI')
    def test_process_query_whitespace(self, mock_chat_openai):
        """Test processing a whitespace-only query"""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        agent = LangGraphAgent()
        
        # Test with whitespace query
        result = asyncio.run(agent.process_query("   "))
        
        self.assertEqual(result["query"], "   ")
        self.assertEqual(result["tool_used"], "llm")
        self.assertIn("Error: Query cannot be empty", result["result"])


if __name__ == '__main__':
    unittest.main() 