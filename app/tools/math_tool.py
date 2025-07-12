import re
import logging
from langchain.tools import tool

# Configure logging
logger = logging.getLogger(__name__)

@tool
def calculate_math(expression: str) -> str:
    """
    Perform mathematical calculations safely.
    
    Args:
        expression: A mathematical expression to evaluate (e.g., "42 * 7", "15 + 27")
    
    Returns:
        The result of the mathematical calculation as a string
    """
    logger.info(f"🧮 Calculating math expression: {expression}")
    
    try:
        # Clean the expression to only allow safe mathematical operations
        cleaned_expr = re.sub(r'[^0-9+\-*/%. ()]', '', expression)
        
        logger.debug(f"🔍 Cleaned expression: '{expression}' -> '{cleaned_expr}'")
        
        if not cleaned_expr:
            error_msg = f"Expression '{expression}' contains no valid mathematical operations"
            logger.error(f"❌ Math validation error: {error_msg}")
            return f"Error: {error_msg}"
        
        result = eval(cleaned_expr)
        result_str = str(result)
        
        logger.info(f"✅ Math result: {expression} = {result_str}")
        return result_str
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logger.error(f"❌ Math calculation error: {error_msg}")
        return error_msg


def extract_math_expression(query: str) -> str:
    """Extract mathematical expression from query for fallback"""
    patterns = [
        r"what is (\d+(?:\s*[\+\-\*\/\*\*\%]\s*\d+)+)",
        r"calculate (\d+(?:\s*[\+\-\*\/\*\*\%]\s*\d+)+)",
        r"(\d+(?:\s*[\+\-\*\/\*\*\%]\s*\d+)+)",
        r"(\d+)\s*(\*|\+|\-|\/|\*\*|\%)\s*(\d+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return "" 