"""
FastAPI Server for AI Operations Assistant
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
import json
import time

from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.verifier import VerifierAgent
from config import Config

# Create FastAPI app
app = FastAPI(
    title="AI Operations Assistant API",
    description="Multi-agent system with real API integrations",
    version="1.0.0"
)

class TaskRequest(BaseModel):
    task: str
    user_id: str = "default"

class AIOpsAssistant:
    """Assistant instance for API"""
    
    def __init__(self):
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.verifier = VerifierAgent()
    
    def process_task(self, user_input: str) -> Dict[str, Any]:
        """Process task end-to-end"""
        start_time = time.time()
        
        # Planning
        plan = self.planner.create_plan(user_input)
        
        # Execution
        results = self.executor.execute_plan(plan)
        
        # Verification
        verification = self.verifier.verify_results(user_input, plan, results)
        
        # Prepare response
        return {
            "task": user_input,
            "execution_time": round(time.time() - start_time, 2),
            "plan": plan,
            "results": results,
            "verification": verification,
            "timestamp": time.time()
        }

# Global assistant instance
assistant = AIOpsAssistant()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI Operations Assistant API",
        "version": "1.0.0",
        "status": "running",
        "agents": ["planner", "executor", "verifier"],
        "apis": ["GitHub API", "Weather API"],
        "endpoints": {
            "GET /": "Service info",
            "POST /process": "Process natural language task",
            "GET /health": "Health check",
            "GET /tools": "List available tools"
        }
    }

@app.post("/process")
async def process_task_api(request: TaskRequest):
    """Process task via API"""
    try:
        result = assistant.process_task(request.task)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/tools")
async def list_tools():
    """List available tools"""
    return {
        "tools": [
            {
                "name": "github_tool",
                "description": "Search GitHub repositories",
                "parameters": {
                    "query": "Search term (string, required)",
                    "per_page": "Number of results (integer, optional, default: 5)"
                }
            },
            {
                "name": "weather_tool",
                "description": "Get current weather",
                "parameters": {
                    "city": "City name (string, required)"
                }
            }
        ]
    }

if __name__ == "__main__":
    print(f"🚀 Starting AI Operations Assistant API on http://{Config.HOST}:{Config.PORT}")
    print(f"📚 API Docs: http://{Config.HOST}:{Config.PORT}/docs")
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)