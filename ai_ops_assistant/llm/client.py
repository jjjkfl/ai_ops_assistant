"""
LLM Client with FREE alternatives (rule-based or local Ollama)
"""
import json
import subprocess
import time
from typing import Dict, Any, Optional, List  # ADDED List here
from config import Config
from utils import extract_city_from_text, extract_query_from_text

class LLMClient:
    """LLM client with FREE alternatives"""
    
    def __init__(self):
        self.use_ollama = self._check_ollama()
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is installed locally"""
        try:
            result = subprocess.run(["ollama", "--version"], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def generate_plan(self, user_input: str) -> Dict[str, Any]:
        """Generate execution plan from user input"""
        
        if self.use_ollama and Config.USE_FREE_LLM:
            return self._generate_with_ollama(user_input)
        else:
            return self._generate_rule_based(user_input)
    
    def _generate_with_ollama(self, user_input: str) -> Dict[str, Any]:
        """Generate plan using local Ollama (FREE)"""
        try:
            system_prompt = """You are an AI Operations Planner. Create a JSON plan with steps.
            
            Available tools:
            1. github_tool: Search GitHub repositories
            2. weather_tool: Get current weather
            
            Return JSON with this structure:
            {
                "plan": [
                    {
                        "step": 1,
                        "description": "step description",
                        "tool": "tool_name",
                        "parameters": {"param": "value"}
                    }
                ],
                "reasoning": "brief reasoning"
            }"""
            
            user_prompt = f"Create an execution plan for: {user_input}"
            
            cmd = ["ollama", "run", Config.OLLAMA_MODEL, 
                  f"System: {system_prompt}\n\nUser: {user_prompt}"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                response = result.stdout.strip()
                # Try to extract JSON
                try:
                    start = response.find('{')
                    end = response.rfind('}') + 1
                    if start != -1 and end != 0:
                        return json.loads(response[start:end])
                except:
                    pass
        
        except Exception as e:
            print(f"Ollama error: {e}")
        
        # Fallback to rule-based
        return self._generate_rule_based(user_input)
    
    def _generate_rule_based(self, user_input: str) -> Dict[str, Any]:
        """Generate plan using rule-based approach (FREE)"""
        user_lower = user_input.lower()
        plan = {"plan": [], "reasoning": ""}
        step_num = 1
        
        # Check for GitHub tasks
        github_keywords = ["github", "repo", "repository", "code", "project", "search", "find"]
        if any(keyword in user_lower for keyword in github_keywords):
            query = extract_query_from_text(user_input)
            plan["plan"].append({
                "step": step_num,
                "description": f"Search GitHub for '{query}' repositories",
                "tool": "github_tool",
                "parameters": {"query": query, "per_page": 5}
            })
            step_num += 1
            plan["reasoning"] += f"User wants to search for {query} repositories. "
        
        # Check for weather tasks
        weather_keywords = ["weather", "temp", "temperature", "forecast", "climate", "humid"]
        if any(keyword in user_lower for keyword in weather_keywords):
            city = extract_city_from_text(user_input)
            plan["plan"].append({
                "step": step_num,
                "description": f"Get current weather in {city}",
                "tool": "weather_tool",
                "parameters": {"city": city}
            })
            step_num += 1
            plan["reasoning"] += f"User wants weather information for {city}. "
        
        # If no steps, add default
        if not plan["plan"]:
            plan["plan"].append({
                "step": 1,
                "description": "Search GitHub for trending AI repositories",
                "tool": "github_tool",
                "parameters": {"query": "artificial intelligence", "per_page": 5}
            })
            plan["reasoning"] = "No specific task mentioned. Providing GitHub search as example."
        
        return plan
    
    def verify_results(self, user_input: str, plan: Dict, results: List[Dict]) -> Dict[str, Any]:
        """Verify execution results"""
        successful = sum(1 for r in results if r.get("success", False))
        total = len(results)
        
        completeness = 100 if total > 0 and successful == total else 50 if successful > 0 else 0
        
        return {
            "is_complete": successful == total,
            "completeness_score": completeness,
            "missing_data": [],
            "suggestions": ["All requirements satisfied"] if successful == total else ["Some steps failed"],
            "summary": f"Completed {successful}/{total} steps successfully"
        }