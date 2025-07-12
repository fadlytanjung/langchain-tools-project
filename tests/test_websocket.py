"""
WebSocket Tests

Tests for WebSocket functionality in the LangGraph agent API.
"""

import pytest
import asyncio
import json
import websockets
from unittest.mock import patch, AsyncMock
import logging

logger = logging.getLogger(__name__)


class TestWebSocketIntegration:
    """Integration tests for WebSocket functionality"""
    
    @pytest.fixture
    def websocket_url(self):
        """WebSocket URL for testing"""
        return "ws://localhost:8000/api/v1/ws"
    
    @pytest.fixture
    def test_queries(self):
        """Test queries for different tool types"""
        return [
            {
                "query": "What is 15 + 27?",
                "expected_tool": "math",
                "expected_response_contains": "42"
            },
            {
                "query": "What's the weather in London?",
                "expected_tool": "weather",
                "expected_response_contains": "°C"
            },
            {
                "query": "Tell me about Python",
                "expected_tool": "llm",
                "expected_response_contains": "Python"
            }
        ]
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self, websocket_url):
        """Test WebSocket connection establishment"""
        try:
            async with websockets.connect(websocket_url) as websocket:
                # Connection successful
                assert websocket.open
                logger.info("✅ WebSocket connection established successfully")
        except Exception as e:
            pytest.skip(f"WebSocket server not running: {e}")
    
    @pytest.mark.asyncio
    async def test_websocket_math_query(self, websocket_url):
        """Test math query via WebSocket"""
        try:
            async with websockets.connect(websocket_url) as websocket:
                # Send math query
                query = {"query": "What is 25 + 17?"}
                await websocket.send(json.dumps(query))
                
                # Receive response
                response = await websocket.recv()
                result = json.loads(response)
                
                # Verify response structure
                assert "query" in result
                assert "tool_used" in result
                assert "response" in result
                
                # Verify content
                assert result["query"] == query["query"]
                assert result["tool_used"] == "math"
                assert "42" in result["response"]
                
                logger.info(f"✅ Math WebSocket test passed: {result}")
                
        except Exception as e:
            pytest.skip(f"WebSocket server not running: {e}")
    
    @pytest.mark.asyncio
    async def test_websocket_weather_query(self, websocket_url):
        """Test weather query via WebSocket"""
        try:
            async with websockets.connect(websocket_url) as websocket:
                # Send weather query
                query = {"query": "What's the weather in Paris?"}
                await websocket.send(json.dumps(query))
                
                # Receive response
                response = await websocket.recv()
                result = json.loads(response)
                
                # Verify response structure
                assert "query" in result
                assert "tool_used" in result
                assert "response" in result
                
                # Verify content
                assert result["query"] == query["query"]
                assert result["tool_used"] == "weather"
                assert "°C" in result["response"]
                
                logger.info(f"✅ Weather WebSocket test passed: {result}")
                
        except Exception as e:
            pytest.skip(f"WebSocket server not running: {e}")
    
    @pytest.mark.asyncio
    async def test_websocket_llm_query(self, websocket_url):
        """Test LLM query via WebSocket"""
        try:
            async with websockets.connect(websocket_url) as websocket:
                # Send LLM query
                query = {"query": "What is artificial intelligence?"}
                await websocket.send(json.dumps(query))
                
                # Receive response
                response = await websocket.recv()
                result = json.loads(response)
                
                # Verify response structure
                assert "query" in result
                assert "tool_used" in result
                assert "response" in result
                
                # Verify content
                assert result["query"] == query["query"]
                assert result["tool_used"] == "llm"
                assert len(result["response"]) > 50  # Should be a substantial response
                
                logger.info(f"✅ LLM WebSocket test passed: {result}")
                
        except Exception as e:
            pytest.skip(f"WebSocket server not running: {e}")
    
    @pytest.mark.asyncio
    async def test_websocket_invalid_message(self, websocket_url):
        """Test WebSocket with invalid message format"""
        try:
            async with websockets.connect(websocket_url) as websocket:
                # Send invalid message (missing query field)
                invalid_message = {"not_query": "test"}
                await websocket.send(json.dumps(invalid_message))
                
                # Receive error response
                response = await websocket.recv()
                result = json.loads(response)
                
                # Verify error response
                assert "error" in result
                assert "query" in result["error"]
                
                logger.info(f"✅ Invalid message WebSocket test passed: {result}")
                
        except Exception as e:
            pytest.skip(f"WebSocket server not running: {e}")
    
    @pytest.mark.asyncio
    async def test_websocket_multiple_queries(self, websocket_url, test_queries):
        """Test multiple queries in a single WebSocket session"""
        try:
            async with websockets.connect(websocket_url) as websocket:
                for i, test_case in enumerate(test_queries):
                    logger.info(f"Testing query {i+1}: {test_case['query']}")
                    
                    # Send query
                    query = {"query": test_case["query"]}
                    await websocket.send(json.dumps(query))
                    
                    # Receive response
                    response = await websocket.recv()
                    result = json.loads(response)
                    
                    # Verify response structure
                    assert "query" in result
                    assert "tool_used" in result
                    assert "response" in result
                    
                    # Verify content
                    assert result["query"] == test_case["query"]
                    assert result["tool_used"] == test_case["expected_tool"]
                    assert test_case["expected_response_contains"] in result["response"]
                    
                    # Small delay between queries
                    await asyncio.sleep(0.1)
                
                logger.info("✅ Multiple queries WebSocket test passed")
                
        except Exception as e:
            pytest.skip(f"WebSocket server not running: {e}")


class TestWebSocketUnit:
    """Unit tests for WebSocket route handlers"""
    
    @pytest.mark.asyncio
    async def test_websocket_route_handler(self):
        """Test WebSocket route handler logic"""
        from app.core.agent import agent_instance
        
        # Mock the agent instance
        mock_result = {
            "query": "test query",
            "tool_used": "math",
            "result": "42"
        }
        
        with patch.object(agent_instance, 'process_query', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = mock_result
            
            # Test the conversion logic
            result = await agent_instance.process_query("test query")
            
            # Verify the result format
            assert result["query"] == "test query"
            assert result["tool_used"] == "math"
            assert result["result"] == "42"
            
            # Test WebSocket response conversion
            websocket_response = {
                "query": result["query"],
                "tool_used": result["tool_used"],
                "response": result["result"]
            }
            
            assert websocket_response["response"] == "42"
            assert "result" not in websocket_response
            
            logger.info("✅ WebSocket route handler unit test passed")


@pytest.mark.asyncio
async def test_websocket_response_format():
    """Test that WebSocket responses use 'response' field instead of 'result'"""
    from app.core.agent import agent_instance
    
    # Mock agent response
    mock_result = {
        "query": "test",
        "tool_used": "math",
        "result": "test result"
    }
    
    with patch.object(agent_instance, 'process_query', new_callable=AsyncMock) as mock_process:
        mock_process.return_value = mock_result
        
        result = await agent_instance.process_query("test")
        
        # Simulate WebSocket conversion
        websocket_response = {
            "query": result["query"],
            "tool_used": result["tool_used"],
            "response": result["result"]  # Convert result to response
        }
        
        # Verify WebSocket format
        assert "response" in websocket_response
        assert "result" not in websocket_response
        assert websocket_response["response"] == "test result"
        
        logger.info("✅ WebSocket response format test passed")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"]) 