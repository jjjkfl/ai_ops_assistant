"""
Planner Agent - Creates execution plans
"""
import json
from typing import Dict, Any
from llm.client import LLMClient

class PlannerAgent:
    """Agent responsible for planning task execution"""
    
    def __init__(self):
        self.llm_client = LLMClient()
    
    def create_plan(self, user_input: str) -> Dict[str, Any]:
        """Create execution plan from user input"""
        print(f"[Planner] Creating plan for: {user_input}")
        
        try:
            plan = self.llm_client.generate_plan(user_input)
            
            # Validate and enhance plan
            validated_plan = self._validate_plan(plan)
            print(f"[Planner] Created plan with {len(validated_plan.get('plan', []))} step(s)")
            
            return validated_plan
            
        except Exception as e:
            print(f"[Planner] Error: {e}")
            return self._create_fallback_plan(user_input)
    
    def _validate_plan(self, plan: Dict) -> Dict:
        """Validate and fix plan structure"""
        if "plan" not in plan:
            plan = {"plan": []}
        
        for i, step in enumerate(plan["plan"]):
            step["step"] = i + 1
            
            # Ensure tool is valid
            if step.get("tool") not in ["github_tool", "weather_tool"]:
                step["tool"] = "github_tool"
            
            # Ensure parameters exist
            if "parameters" not in step:
                step["parameters"] = {}
            
            # Set default parameters based on tool
            if step["tool"] == "github_tool":
                if "query" not in step["parameters"]:
                    step["parameters"]["query"] = "python"
                if "per_page" not in step["parameters"]:
                    step["parameters"]["per_page"] = 5
            
            elif step["tool"] == "weather_tool":
                if "city" not in step["parameters"]:
                    step["parameters"]["city"] = "London"
        
        return plan
    
    def _create_fallback_plan(self, user_input: str) -> Dict:
        """Create fallback plan"""
        return {
            "plan": [
                {
                    "step": 1,
                    "description": "Search GitHub repositories",
                    "tool": "github_tool",
                    "parameters": {"query": "python", "per_page": 5}
                }
            ],
            "reasoning": "Fallback plan created",
            "note": "Using fallback planning"
        }