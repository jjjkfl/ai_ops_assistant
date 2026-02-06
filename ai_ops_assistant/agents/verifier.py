"""
Verifier Agent - Validates and formats results
"""
import json
import time
from typing import Dict, Any, List  # ADDED List here
from llm.client import LLMClient

class VerifierAgent:
    """Agent responsible for verifying execution results"""
    
    def __init__(self):
        self.llm_client = LLMClient()
    
    def verify_results(self, 
                      user_input: str, 
                      plan: Dict, 
                      results: List[Dict]) -> Dict[str, Any]:
        """Verify execution results and format final output"""
        
        print(f"[Verifier] Verifying {len(results)} result(s)")
        
        # Separate successful and failed results
        successful_results = [r for r in results if r.get("success", False)]
        failed_results = [r for r in results if not r.get("success", False)]
        
        if not successful_results:
            return self._handle_all_failed(failed_results, user_input)
        
        # Use LLM for verification
        verification = self.llm_client.verify_results(user_input, plan, results)
        
        # Build final output
        final_output = self._build_final_output(
            user_input=user_input,
            plan=plan,
            successful_results=successful_results,
            failed_results=failed_results,
            verification=verification
        )
        
        return {
            "verification": verification,
            "final_output": final_output,
            "summary": {
                "total_steps": len(plan.get("plan", [])),
                "successful_steps": len(successful_results),
                "failed_steps": len(failed_results),
                "completeness_score": verification.get("completeness_score", 0)
            }
        }
    
    def _handle_all_failed(self, failed_results: List[Dict], user_input: str) -> Dict[str, Any]:
        """Handle case where all steps failed"""
        return {
            "verification": {
                "is_complete": False,
                "completeness_score": 0,
                "missing_data": ["All execution steps failed"],
                "suggestions": ["Check API availability", "Verify parameters", "Try different tools"],
                "summary": f"Failed to execute task: {user_input}"
            },
            "final_output": {
                "status": "failed",
                "user_request": user_input,
                "errors": [r.get("error", "Unknown error") for r in failed_results],
                "suggestions": [
                    "Try rephrasing your request",
                    "Check if the requested information is available",
                    "Try a simpler request first"
                ]
            }
        }
    
    def _build_final_output(self, **kwargs) -> Dict[str, Any]:
        """Build final structured output"""
        
        # Extract data from successful results
        formatted_data = []
        
        for result in kwargs["successful_results"]:
            if result.get("tool") == "github_tool":
                data = result.get("data", {})
                formatted_data.append({
                    "type": "github",
                    "query": data.get("query", ""),
                    "repositories": data.get("repositories", []),
                    "total_count": data.get("total_count", 0),
                    "source": data.get("source", "unknown"),
                    "cached": result.get("cached", False)
                })
                
            elif result.get("tool") == "weather_tool":
                data = result.get("data", {})
                formatted_data.append({
                    "type": "weather",
                    "city": data.get("city", ""),
                    "country": data.get("country", ""),
                    "temperature": data.get("temperature", 0),
                    "condition": data.get("condition", ""),
                    "humidity": data.get("humidity", 0),
                    "wind_speed": data.get("wind_speed", 0),
                    "source": data.get("source", "unknown"),
                    "cached": result.get("cached", False)
                })
        
        return {
            "task_execution": {
                "user_request": kwargs["user_input"],
                "status": "completed" if kwargs["verification"].get("is_complete", False) else "partial",
                "completeness_score": kwargs["verification"].get("completeness_score", 0),
                "execution_time": time.time(),
                "plan_summary": {
                    "total_steps": len(kwargs["plan"].get("plan", [])),
                    "executed_steps": len(kwargs["successful_results"]),
                    "failed_steps": len(kwargs["failed_results"])
                }
            },
            "results": formatted_data,
            "verification": {
                "is_complete": kwargs["verification"].get("is_complete", False),
                "score": kwargs["verification"].get("completeness_score", 0),
                "issues": kwargs["verification"].get("missing_data", []),
                "suggestions": kwargs["verification"].get("suggestions", [])
            },
            "metadata": {
                "system": "AI Operations Assistant",
                "version": "1.0.0",
                "architecture": "multi-agent",
                "timestamp": time.time(),
                "agents_used": ["planner", "executor", "verifier"]
            }
        }