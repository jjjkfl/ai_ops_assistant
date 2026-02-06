"""
Base tool class with common functionality
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
import json
import hashlib

class BaseTool(ABC):
    """Abstract base class for all tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        pass
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate input parameters"""
        return True
    
    def get_cache_key(self, **kwargs) -> str:
        """Generate cache key from parameters"""
        params_str = json.dumps(kwargs, sort_keys=True)
        return hashlib.md5(params_str.encode()).hexdigest()
    
    def get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available"""
        if cache_key in self.cache:
            cached_item = self.cache[cache_key]
            if time.time() - cached_item["timestamp"] < self.cache_ttl:
                return cached_item["result"]
        return None
    
    def cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Cache a result"""
        self.cache[cache_key] = {
            "result": result,
            "timestamp": time.time()
        }
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description}"