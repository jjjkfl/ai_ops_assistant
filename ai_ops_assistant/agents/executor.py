"""
Executor Agent - Executes plan steps
"""
import time
from typing import Dict, Any, List  # ADDED List here
from tools.github_tool import GitHubTool
from tools.weather_tool import WeatherTool
from config import Config

class ExecutorAgent:
    """Agent responsible for executing plan steps"""
    
    def __init__(self):
        self.tools = {
            "github_tool": GitHubTool(),
            "weather_tool": WeatherTool()
        }
        self.execution_history = []
    
    def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step"""
        tool_name = step.get("tool")
        parameters = step.get("parameters", {})
        
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found",
                "step": step
            }
        
        tool = self.tools[tool_name]
        
        # Validate parameters
        if not tool.validate_parameters(**parameters):
            return {
                "success": False,
                "error": f"Invalid parameters for {tool_name}",
                "parameters": parameters,
                "step": step
            }
        
        # Execute with retry
        for attempt in range(Config.MAX_RETRIES):
            try:
                print(f"[Executor] Executing step {step['step']} (Attempt {attempt + 1})")
                result = tool.execute(**parameters)
                result["step"] = step["step"]
                result["tool"] = tool_name
                
                # Add to history
                self.execution_history.append({
                    "step": step["step"],
                    "tool": tool_name,
                    "result": result,
                    "timestamp": time.time()
                })
                
                return result
                
            except Exception as e:
                print(f"[Executor] Attempt {attempt + 1} failed: {e}")
                if attempt < Config.MAX_RETRIES - 1:
                    time.sleep(Config.RETRY_DELAY)
                else:
                    return {
                        "success": False,
                        "error": f"Failed after {Config.MAX_RETRIES} attempts: {str(e)}",
                        "step": step,
                        "tool": tool_name
                    }
        
        return {
            "success": False,
            "error": "Execution failed",
            "step": step
        }
    
    def execute_plan(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute entire plan"""
        results = []
        
        for step in plan.get("plan", []):
            result = self.execute_step(step)
            results.append(result)
            
            # Small delay between steps to avoid rate limiting
            time.sleep(0.5)
        
        return results
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get execution summary"""
        successful = [r for r in self.execution_history if r.get("result", {}).get("success", False)]
        failed = [r for r in self.execution_history if not r.get("result", {}).get("success", False)]
        
        return {
            "total_executions": len(self.execution_history),
            "successful": len(successful),
            "failed": len(failed),
            "tools_used": list(set([h["tool"] for h in self.execution_history]))
        }