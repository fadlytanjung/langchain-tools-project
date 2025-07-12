from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from ..models.schemas import QueryRequest, QueryResponse
from ..core.agent import agent_instance
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a user query and route it to the appropriate tool"""
    logger.info(f"📨 Received query request: {request.query}")
    
    try:
        result = await agent_instance.process_query(request.query)
        logger.info(f"✅ Query processed successfully. Tool: {result['tool_used']}")
        return QueryResponse(**result)
    except Exception as e:
        logger.error(f"❌ Error processing query: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": str(e)
            }
        )

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time query processing"""
    logger.info("🔌 WebSocket connection initiated")
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if "query" not in message:
                logger.warning("⚠️ WebSocket message missing 'query' field")
                await websocket.send_text(json.dumps({
                    "error": "Missing 'query' field in message"
                }))
                continue
            
            logger.info(f"📨 WebSocket query received: {message['query']}")
            
            # Process the query
            try:
                result = await agent_instance.process_query(message["query"])
                logger.info(f"✅ WebSocket query processed. Tool: {result['tool_used']}")
                
                # Convert result to response for WebSocket
                websocket_response = {
                    "query": result["query"],
                    "tool_used": result["tool_used"],
                    "response": result["result"]
                }
                await websocket.send_text(json.dumps(websocket_response))
            except Exception as e:
                logger.error(f"❌ WebSocket query error: {str(e)}")
                await websocket.send_text(json.dumps({
                    "error": "Error processing query",
                    "message": str(e)
                }))
                
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket client disconnected")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        await websocket.close() 