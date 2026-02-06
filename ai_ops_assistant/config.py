"""
Configuration for AI Operations Assistant
"""
import os
from typing import Dict, Any

class Config:
    """Application configuration"""
    
    # FREE APIs - No keys required for basic functionality
    GITHUB_API_BASE = "https://api.github.com"
    WEATHER_API_BASE = "https://api.open-meteo.com/v1"
    
    # For enhanced features (optional)
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    
    # LLM Configuration - Using FREE alternatives
    USE_FREE_LLM = True  # Use rule-based instead of paid LLM
    OLLAMA_MODEL = "llama3.2"  # If using local Ollama
    
    # Application Settings
    HOST = "localhost"
    PORT = 8000
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0
    REQUEST_TIMEOUT = 30
    
    # Cache Settings
    CACHE_ENABLED = True
    CACHE_TTL = 300  # 5 minutes
    
    @classmethod
    def get_github_headers(cls) -> Dict[str, str]:
        """Get GitHub API headers"""
        return {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Operations-Assistant"
        }