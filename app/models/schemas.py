from pydantic import BaseModel


class QueryRequest(BaseModel):
    """Request model for user queries"""
    query: str


class QueryResponse(BaseModel):
    """Response model for tool execution results"""
    query: str
    tool_used: str
    result: str


class WeatherResponse(BaseModel):
    """Weather API response model"""
    temperature: float
    description: str
    city: str
    country: str


class MathResponse(BaseModel):
    """Math operation response model"""
    expression: str
    result: float
    operation: str


class LLMResponse(BaseModel):
    """LLM response model"""
    answer: str
    model_used: str 