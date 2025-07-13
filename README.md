# LangChain Tools API

A FastAPI backend application that routes natural language queries to appropriate tools using LangGraph and LangChain. The application can handle weather queries, mathematical calculations, and general questions using an LLM.

## Features

- **Smart Query Routing**: Automatically routes queries to the appropriate tool based on content using LangGraph
- **Weather Tool**: Fetches weather information using OpenWeatherMap API
- **Math Tool**: Performs mathematical calculations safely
- **LLM Agent**: Answers general questions using OpenAI's GPT models
- **RESTful API**: Clean HTTP endpoints for query processing
- **WebSocket Support**: Real-time query processing via WebSocket connections
- **Comprehensive Testing**: Unit tests for all components including WebSocket functionality
- **Docker Support**: Containerized application for easy deployment

## Project Structure

```
langchain-tools-project/
├── app/
│   ├── api/
│   │   └── routes.py          # FastAPI routes
│   ├── core/
│   │   ├── agent.py           # LangGraph agent with tool routing
│   │   └── config.py          # Configuration settings
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   ├── tools/
│   │   ├── weather_tool.py    # Weather API integration
│   │   ├── math_tool.py       # Mathematical operations
│   │   └── __init__.py        # Tool exports
│   └── main.py                # FastAPI application
├── tests/
│   ├── test_agent.py          # Agent unit tests
│   ├── test_api.py            # API endpoint tests
│   ├── test_tools.py          # Tool functionality tests
│   ├── test_basic.py          # Basic integration tests
│   ├── test_websocket.py      # WebSocket functionality tests
│   ├── conftest.py            # Test configuration
│   └── __init__.py            # Test package
├── main.py                    # Application entry point
├── run_tests.py               # Test runner script
├── graph-notebook.ipynb       # Jupyter notebook for testing
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
└── README.md                  # This file
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- OpenAI API key (for LLM functionality)
- OpenWeatherMap API key (optional, for real weather data)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd langchain-tools-project
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```bash
   # OpenAI (Required)
   OPENAI_API_KEY=your_openai_api_key_here
   DEFAULT_MODEL=gpt-4o-mini
   
   # OpenWeatherMap (Optional - uses mock data if not provided)
   OPENWEATHER_API_KEY=your_openweather_api_key_here
   OPENWEATHER_BASE_URL=https://api.openweathermap.org/data/2.5/weather
   
   # LangChain/Smith Tracing (Optional)
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
   LANGCHAIN_API_KEY=your_langchain_api_key_here
   LANGCHAIN_PROJECT=your_project_name
   
   # App Configuration
   APP_NAME=LangChain Tools API
   ```

4. **Run the application**
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`

### API Documentation with Swagger

Once the application is running, you can access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

The Swagger UI provides an interactive interface where you can:
- View all available endpoints
- Test API calls directly from the browser
- See request/response schemas
- Try out different queries and see the responses

### Using Docker

1. **Build the Docker image**
   ```bash
   docker build -t langchain-tools-api .
   ```

2. **Run the container**
   ```bash
   docker run -p 8000:8000 --env-file .env langchain-tools-api
   ```

## API Documentation

> **💡 Tip**: For interactive API testing, visit http://localhost:8000/docs to use the Swagger UI interface.

### Endpoints

#### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

#### POST `/api/v1/query`
Process a natural language query and route it to the appropriate tool.

**Request Body:**
```json
{
  "query": "What's the weather like today in Paris?"
}
```

**Response:**
```json
{
  "query": "What's the weather like today in Paris?",
  "tool_used": "weather",
  "result": "It's sunny and 26°C in Paris, FR."
}
```

#### WebSocket `/api/v1/ws`
Real-time query processing via WebSocket connection.

**Message Format:**
```json
{
  "query": "What is 25 + 17?"
}
```

**Response Format:**
```json
{
  "query": "What is 25 + 17?",
  "tool_used": "math",
  "response": "42"
}
```

**Note:** WebSocket responses use `response` field instead of `result` field used in REST API.

### Tool Examples

#### Weather Tool
- **Input**: "What's the weather in Tokyo?"
- **Tool Used**: `weather`
- **Output**: Current weather conditions for Tokyo

#### Math Tool
- **Input**: "What is 42 * 7?"
- **Tool Used**: `math`
- **Output**: "294"

#### LLM Tool
- **Input**: "Who is the president of France?"
- **Tool Used**: `llm`
- **Output**: "Emmanuel Macron is the president of France."

## API Examples

### Using curl

```bash
# Health check
curl -X GET "http://localhost:8000/health"

# Weather query
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather in Tokyo?"}'

# Math query
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Calculate 15 + 27"}'

# General question
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the capital of Japan?"}'

```

### Using Python

#### REST API
```python
import requests
import json

# API endpoint
url = "http://localhost:8000/api/v1/query"

# Example queries
queries = [
    "What's the weather like in Paris?",
    "What is 42 * 7?",
    "Who is the president of France?"
]

for query in queries:
    response = requests.post(url, json={"query": query})
    result = response.json()
    print(f"Query: {result['query']}")
    print(f"Tool: {result['tool_used']}")
    print(f"Result: {result['result']}")
    print("-" * 50)
```

#### WebSocket
```python
import asyncio
import json
import websockets

async def test_websocket():
    uri = "ws://localhost:8000/api/v1/ws"
    
    async with websockets.connect(uri) as websocket:
        # Send query
        query = {"query": "What is 15 + 27?"}
        await websocket.send(json.dumps(query))
        
        # Receive response
        response = await websocket.recv()
        result = json.loads(response)
        
        print(f"Query: {result['query']}")
        print(f"Tool: {result['tool_used']}")
        print(f"Response: {result['response']}")

# Run the WebSocket test
asyncio.run(test_websocket())
```

## Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Using the test runner (recommended)
python run_tests.py --basic          # Run basic tests
python run_tests.py --websocket      # Run WebSocket tests
python run_tests.py --all            # Run all tests
python run_tests.py --coverage       # Run with coverage
python run_tests.py --verbose        # Verbose output with debug logging

# Using pytest directly
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_basic.py -v
python -m pytest tests/test_agent.py -v
python -m pytest tests/test_api.py -v
python -m pytest tests/test_tools.py -v
python -m pytest tests/test_websocket.py -v

# Run tests with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

### Test Structure

- **`test_basic.py`**: Basic integration tests and imports
- **`test_agent.py`**: LangGraph agent functionality and routing
- **`test_api.py`**: FastAPI endpoints and request/response handling
- **`test_tools.py`**: Individual tool functionality
- **`test_websocket.py`**: WebSocket connection and message handling
- **`conftest.py`**: Test configuration and fixtures

### Test Coverage

The test suite covers:
- ✅ Tool imports and functionality
- ✅ Agent routing logic
- ✅ API endpoint responses
- ✅ WebSocket connections and messaging
- ✅ Error handling
- ✅ Input validation
- ✅ Health checks

## Architecture

### LangGraph Agent

The application uses LangGraph to create a sophisticated routing system:

```python
# Graph structure:
START → Router → [Math Tool | Weather Tool | LLM Agent] → END
```

1. **Router Node**: Analyzes query and determines appropriate tool
2. **Tool Nodes**: Execute specific functionality (math, weather)
3. **LLM Node**: Handles general questions directly

### Tool System

Each tool is implemented as a LangChain tool with:
- **Function signature**: Defined with `@tool` decorator
- **Input validation**: Pydantic models for type safety
- **Error handling**: Graceful error responses
- **Logging**: Comprehensive logging for debugging

## Configuration

The application can be configured through environment variables:

**Required:**
- `OPENAI_API_KEY`: Required for LLM functionality
- `DEFAULT_MODEL`: OpenAI model to use (default: gpt-4o-mini)

**Optional:**
- `OPENWEATHER_API_KEY`: For real weather data (uses mock if not provided)
- `LANGCHAIN_API_KEY`: For LangSmith tracing
- `LANGCHAIN_PROJECT`: Project name for LangSmith
- `LANGCHAIN_TRACING_V2`: Enable LangSmith tracing
- `APP_NAME`: Application name (default: LangChain Tools API)

## Development

### Interactive Testing

The project includes a Jupyter notebook (`graph-notebook.ipynb`) for interactive testing and experimentation:

```bash
# Install Jupyter (if not already installed)
pip install jupyter

# Start Jupyter notebook
jupyter notebook

# Open graph-notebook.ipynb
```

The notebook provides:
- Interactive agent testing
- Step-by-step tool execution
- Graph visualization
- Custom query testing

### Code Structure

- **Agent**: LangGraph-based routing with separate nodes for each tool type
- **Tools**: LangChain tools with proper input/output schemas
- **API**: FastAPI with automatic OpenAPI documentation
- **Config**: Centralized configuration management
- **Tests**: Comprehensive unit and integration tests

### Adding New Tools

1. Create a new tool file in `app/tools/`
2. Implement using `@tool` decorator
3. Add to `app/tools/__init__.py`
4. Update agent to include new tool
5. Add tests for the new tool

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## Deployment

### Production Considerations

- Set `OPENAI_API_KEY` securely
- Configure proper logging levels
- Use environment-specific configuration
- Monitor API usage and costs
- Implement rate limiting if needed

### Docker Deployment

The application includes a Dockerfile for containerized deployment:

```bash
# Build and run
docker build -t langchain-tools-api .
docker run -p 8000:8000 --env-file .env langchain-tools-api
```

## License

This project is licensed under the MIT License. 