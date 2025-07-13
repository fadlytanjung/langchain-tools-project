import os
import logging
from typing import TypedDict, Optional, List
from typing_extensions import Literal
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from ..core.config import settings
from ..tools import get_weather, calculate_math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# State Definition
class AgentState(TypedDict, total=False):
    messages: List[BaseMessage]
    tool_used: Optional[Literal["weather", "math", "llm"]]
    result: Optional[str]

class LangGraphAgent:
    def __init__(self):
        logger.info("🚀 Initializing LangGraphAgent")
        
        if not settings.OPENAI_API_KEY:
            logger.error("❌ OpenAI API key is missing")
            raise ValueError("OpenAI API key is required")
        
        if not settings.DEFAULT_MODEL:
            logger.error("❌ Default model is not specified")
            raise ValueError("Default model must be specified")
        
        # Setup LLM
        os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
        self.llm = ChatOpenAI(model=settings.DEFAULT_MODEL, temperature=0)
        self.llm_with_tools = self.llm.bind_tools([get_weather, calculate_math])
        
        logger.info(f"🤖 LLM initialized with model: {settings.DEFAULT_MODEL}")
        
        # Build graph
        self.graph = self._build_graph()
        logger.info("📊 Graph built successfully")

    def agent(self, state: AgentState) -> AgentState:
        """Agent node for handling general LLM queries without tools."""
        logger.info("🧠 Processing LLM query (no tools)")
        
        messages = state.get("messages", [])
        if not messages:
            logger.error("❌ No messages found in state")
            state["result"] = "No messages to process"
            state["tool_used"] = "llm"
            return state
        
        logger.debug(f"📨 Processing {len(messages)} messages")
        
        try:
            result = self.llm.invoke(messages)
            
            # Handle content that might be string or list
            content = result.content
            if isinstance(content, list):
                logger.debug("🔄 Converting list content to string")
                content = str(content)
            
            state["result"] = content
            state["tool_used"] = "llm"
            
            logger.info(f"✅ LLM result: {content[:100]}{'...' if len(content) > 100 else ''}")
            
        except Exception as e:
            error_msg = f"Error processing LLM query: {str(e)}"
            logger.error(f"❌ LLM processing error: {error_msg}")
            state["result"] = error_msg
            state["tool_used"] = "llm"
        
        return state

    def agent_with_tools(self, state: AgentState) -> AgentState:
        """Agent node that can use tools - LLM handles tool call extraction, we execute the tool."""
        logger.info("🛠️  Processing query with tools available")
        
        messages = state.get("messages", [])
        if not messages:
            logger.error("❌ No messages found in state")
            state["result"] = "No messages to process"
            state["tool_used"] = "llm"
            return state

        logger.debug(f"📨 Processing {len(messages)} messages with tools")

        tool_registry = {
            "get_weather": get_weather,
            "calculate_math": calculate_math,
        }

        try:
            result = self.llm_with_tools.invoke(messages)
            logger.info(f"🔍 LLM tool call result: {result}")

            if (
                isinstance(result, AIMessage)
                and hasattr(result, "tool_calls")
                and result.tool_calls
            ):
                logger.info(f"🔧 Tool calls detected: {len(result.tool_calls)} calls")

                tool_call = result.tool_calls[0]
                tool_name = tool_call.get("name", "")
                tool_args = tool_call.get("args", {})

                logger.info(f"🎯 Executing tool: {tool_name} with args: {tool_args}")

                if tool_name in tool_registry:
                    state["result"] = tool_registry[tool_name].invoke(tool_args)
                    # Set tool_used to the actual tool name (math or weather)
                    if tool_name == "get_weather":
                        state["tool_used"] = "weather"
                    elif tool_name == "calculate_math":
                        state["tool_used"] = "math"
                    else:
                        state["tool_used"] = "llm"
                else:
                    logger.warning(f"⚠️  Unknown tool name: {tool_name}")
                    state["result"] = f"Unknown tool: {tool_name}"
                    state["tool_used"] = "llm"
            else:
                logger.info("📝 No tools called, returning LLM response")
                state["tool_used"] = "llm"
                content = result.content
                if isinstance(content, list):
                    content = str(content)
                state["result"] = content

            logger.info(
                f"✅ Tool execution complete. Tool used: {state.get('tool_used')}"
            )

        except Exception as e:
            error_msg = f"Error processing query with tools: {str(e)}"
            logger.error(f"❌ Tool processing error: {error_msg}")
            state["result"] = error_msg
            state["tool_used"] = "llm"

        return state

    def llm_call_router(self, state: AgentState) -> AgentState:
        """Route queries to appropriate tools based on content analysis."""
        logger.info("🧭 Routing query to appropriate tool")
        
        messages = state.get("messages", [])
        if not messages:
            logger.error("❌ No messages found in state")
            state["tool_used"] = "llm"
            return state
        
        human_message = next((msg for msg in reversed(messages) if isinstance(msg, HumanMessage)), None)
        if human_message is None:
            logger.error("❌ No HumanMessage found in messages")
            state["tool_used"] = "llm"
            return state
        
        logger.debug(f"🔍 Routing query: {human_message.content}")
        
        try:
            decision = self.llm.invoke([
                SystemMessage(content="Route the query to weather, math, or llm based on the user's request. Respond with only one word: 'weather', 'math', or 'llm'."),
                human_message,
            ])
            
            # Handle content that might be string or list
            content = decision.content
            if isinstance(content, list):
                logger.debug("🔄 Converting routing decision list to string")
                content = str(content)
            
            decision_text = content.strip().lower()
            logger.info(f"🎯 Routing decision: '{decision_text}'")
            
            # Set tool_used based on decision
            if decision_text == "weather":
                state["tool_used"] = "weather"
            elif decision_text == "math":
                state["tool_used"] = "math"
            else:
                state["tool_used"] = "llm"
            
            logger.info(f"✅ Query routed to: {state['tool_used']}")
            
        except Exception as e:
            logger.error(f"❌ Routing error: {str(e)}")
            state["tool_used"] = "llm"  # Default fallback
        
        return state

    def route_decision(self, state: AgentState) -> str:
        """Determine which path to take based on router decision."""
        logger.debug("🔀 Making routing decision")
        
        tool_used = state.get("tool_used", "llm")
        result = tool_used or "llm"
        
        logger.debug(f"🎯 Route decision: {result}")
        return result

    def _build_graph(self) -> CompiledStateGraph:
        """Build the graph exactly like the notebook version."""
        logger.info("🏗️  Building graph structure")
        
        graph_builder = StateGraph(AgentState)
        
        # Add nodes
        graph_builder.add_node("llm", self.agent)
        graph_builder.add_node("tools", self.agent_with_tools)
        graph_builder.add_node("router", self.llm_call_router)
        
        logger.debug("📊 Added nodes: llm, tools, router")
        
        # Add edges - exactly like notebook
        graph_builder.add_edge(START, "router")
        graph_builder.add_conditional_edges(
            "router",
            self.route_decision,
            {
                "math": "tools",
                "weather": "tools",
                "llm": "llm",
            },
        )
        
        graph_builder.add_edge("llm", END)
        graph_builder.add_edge("tools", END)
        
        logger.debug("🔗 Added edges: START->router, router->[math/weather->tools, llm->llm], [llm/tools]->END")
        
        compiled_graph = graph_builder.compile()
        logger.info("✅ Graph compilation complete")
        return compiled_graph

    async def process_query(self, query: str) -> dict:
        """Process a query through the agent graph."""
        logger.info(f"🚀 Processing query: {query}")
        
        if not query or not query.strip():
            logger.error("❌ Empty query provided")
            return {
                "query": query,
                "tool_used": "llm",
                "result": "Error: Query cannot be empty"
            }
        
        try:
            state: AgentState = {
                "messages": [HumanMessage(content=query)],
            }
            
            logger.debug("📊 Starting graph execution")
            final_state = await self.graph.ainvoke(state)
            
            result = {
                "query": query,
                "tool_used": final_state.get("tool_used", ""),
                "result": final_state.get("result", "")
            }
            
            logger.info(f"✅ Query processed successfully. Tool: {result['tool_used']}, Result length: {len(result['result'])}")
            return result
            
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            logger.error(f"❌ Query processing error: {error_msg}")
            return {
                "query": query,
                "tool_used": "llm",
                "result": error_msg
            }

# Create global instance
logger.info("🌟 Creating global agent instance")
agent_instance = LangGraphAgent()

# API Handler functions for backward compatibility
async def process_query(query: str) -> dict:
    """Process a query through the agent graph."""
    return await agent_instance.process_query(query)

def create_agent():
    """Create and return the agent graph and process function."""
    return agent_instance.graph, process_query 