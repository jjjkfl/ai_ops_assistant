"""
Utility functions for AI Operations Assistant
"""
import json
import time
import hashlib
from typing import Dict, Any, Optional
import requests
from functools import wraps

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retrying failed API calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator

def format_response(data: Any, success: bool = True, error: Optional[str] = None) -> Dict[str, Any]:
    """Format standardized API response"""
    return {
        "success": success,
        "data": data,
        "error": error,
        "timestamp": time.time()
    }

def extract_city_from_text(text: str) -> str:
    """Extract city name from natural language text"""
    import re
    
    cities = [
        "tokyo", "london", "new york", "paris", "berlin", "mumbai",
        "delhi", "beijing", "shanghai", "dubai", "singapore", "sydney",
        "san francisco", "los angeles", "chicago", "toronto", "moscow",
        "rome", "madrid", "amsterdam", "vienna", "prague", "budapest"
    ]
    
    text_lower = text.lower()
    
    # Check for exact city names
    for city in cities:
        if city in text_lower:
            return city.title()
    
    # Try pattern matching
    patterns = [
        r"in\s+([A-Za-z\s]+?)(?:\s|$|,)",
        r"at\s+([A-Za-z\s]+?)(?:\s|$|,)",
        r"for\s+([A-Za-z\s]+?)(?:\s|$|,)",
        r"weather\s+in\s+([A-Za-z\s]+?)(?:\s|$|,)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            potential_city = match.group(1).strip().title()
            if len(potential_city.split()) <= 3:
                return potential_city
    
    return "London"  # Default

def extract_query_from_text(text: str) -> str:
    """Extract search query from natural language text"""
    text_lower = text.lower()
    
    # Programming languages
    languages = ["python", "javascript", "java", "typescript", "go", "rust", "php", "swift", "c++", "c#"]
    for lang in languages:
        if lang in text_lower:
            return lang
    
    # Tech topics
    topics = [
        "machine learning", "artificial intelligence", "ai", "ml",
        "deep learning", "web development", "data science",
        "blockchain", "iot", "cloud computing", "devops"
    ]
    for topic in topics:
        if topic in text_lower:
            return topic
    
    # Default based on common words
    if "github" in text_lower or "repo" in text_lower:
        return "open source"
    
    return "ai"  # Default