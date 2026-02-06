"""
Main entry point for AI Operations Assistant (CLI)
"""
import json
import time
import argparse
import sys
from typing import Dict, Any

from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.verifier import VerifierAgent
from config import Config

class AIOpsAssistant:
    """Main orchestrator for the AI Operations Assistant"""
    
    def __init__(self):
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.verifier = VerifierAgent()
        
        print("=" * 70)
        print("🤖 AI OPERATIONS ASSISTANT")
        print("=" * 70)
        print("✅ Multi-agent system with REAL APIs")
        print("📋 Agents: Planner, Executor, Verifier")
        print("🔌 APIs: GitHub API, Weather API (FREE)")
        print("🎯 No API keys required for basic functionality")
        print("=" * 70)
    
    def process_task(self, user_input: str) -> Dict[str, Any]:
        """Main processing pipeline"""
        
        print(f"\n📋 TASK: {user_input}")
        print("-" * 70)
        
        start_time = time.time()
        
        # Step 1: Planning
        print("\n[1/3] 📋 PLANNING")
        print("-" * 30)
        plan = self.planner.create_plan(user_input)
        print(f"✓ Plan created: {len(plan.get('plan', []))} step(s)")
        
        if plan.get('reasoning'):
            print(f"  Reasoning: {plan['reasoning'][:100]}...")
        
        # Step 2: Execution
        print("\n[2/3] ⚡ EXECUTION")
        print("-" * 30)
        results = self.executor.execute_plan(plan)
        
        successful = sum(1 for r in results if r.get("success", False))
        failed = len(results) - successful
        print(f"✓ Execution complete: {successful} successful, {failed} failed")
        
        # Step 3: Verification
        print("\n[3/3] ✅ VERIFICATION")
        print("-" * 30)
        verification_result = self.verifier.verify_results(user_input, plan, results)
        
        completeness = verification_result["verification"].get("completeness_score", 0)
        print(f"✓ Verification complete: {completeness}/100 completeness score")
        
        # Prepare final response
        execution_time = time.time() - start_time
        
        final_response = {
            "request": user_input,
            "execution_time": round(execution_time, 2),
            "plan": plan,
            "execution_results": results,
            "verification": verification_result["verification"],
            "final_output": verification_result["final_output"],
            "summary": verification_result.get("summary", {})
        }
        
        return final_response
    
    def display_results(self, results: Dict[str, Any]):
        """Display formatted results"""
        
        output = results["final_output"]
        
        print("\n" + "=" * 70)
        print("📊 FINAL RESULTS")
        print("=" * 70)
        
        print(f"\n📝 Task: {output['task_execution']['user_request']}")
        print(f"✅ Status: {output['task_execution']['status'].upper()}")
        print(f"📈 Completeness: {output['task_execution']['completeness_score']}/100")
        print(f"📊 Steps: {output['task_execution']['plan_summary']['executed_steps']}/{output['task_execution']['plan_summary']['total_steps']} successful")
        
        # Display results by type
        for result in output.get("results", []):
            if result["type"] == "github":
                print(f"\n🔍 GITHUB RESULTS")
                print("-" * 40)
                
                if result.get("query"):
                    print(f"  Search Query: '{result['query']}'")
                
                if result.get("total_count", 0) > 0:
                    print(f"  Total Found: {result['total_count']} repositories")
                    print(f"  Showing: {result.get('count', len(result.get('repositories', [])))} repositories")
                
                for i, repo in enumerate(result.get("repositories", [])[:3], 1):
                    print(f"\n  {i}. {repo.get('name', 'Unknown')}")
                    print(f"     Description: {repo.get('description', 'No description')}")
                    print(f"     ⭐ Stars: {repo.get('stars', 0)} | 🍴 Forks: {repo.get('forks', 0)}")
                    print(f"     Language: {repo.get('language', 'Unknown')}")
                    print(f"     URL: {repo.get('url', 'No URL')}")
            
            elif result["type"] == "weather":
                print(f"\n🌤️  WEATHER RESULTS")
                print("-" * 40)
                
                print(f"  Location: {result.get('city', 'Unknown')}, {result.get('country', '')}")
                
                if result.get("temperature"):
                    print(f"  🌡️  Temperature: {result['temperature']}°C")
                    if result.get("feels_like"):
                        print(f"     Feels like: {result['feels_like']}°C")
                
                if result.get("condition"):
                    print(f"  ☁️  Condition: {result['condition']}")
                
                if result.get("humidity"):
                    print(f"  💧 Humidity: {result['humidity']}%")
                
                if result.get("wind_speed"):
                    print(f"  💨 Wind: {result['wind_speed']} km/h")
        
        print(f"\n⏱️  Execution Time: {results['execution_time']} seconds")
        
        print("\n" + "=" * 70)
        print("✅ PROCESSING COMPLETE")
        print("=" * 70)

def run_cli():
    """Run assistant in CLI mode"""
    
    parser = argparse.ArgumentParser(
        description="AI Operations Assistant - Multi-agent system with real APIs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "Find Python AI repositories on GitHub"
  python main.py "What's the weather in Tokyo and London?"
  python main.py "Get weather forecast for Paris and search for machine learning projects"
  python main.py --interactive
  python main.py --example
        """
    )
    
    parser.add_argument("task", nargs="?", help="Natural language task to execute")
    parser.add_argument("--interactive", "-i", action="store_true", help="Start interactive mode")
    parser.add_argument("--example", "-e", action="store_true", help="Run example tasks")
    parser.add_argument("--output", "-o", help="Save results to JSON file")
    
    args = parser.parse_args()
    
    # Initialize assistant
    assistant = AIOpsAssistant()
    
    # Run example tasks
    if args.example:
        print("\n📚 RUNNING EXAMPLE TASKS")
        print("=" * 70)
        
        examples = [
            "Find Python machine learning repositories",
            "What's the current weather in Tokyo?",
            "Check London weather and find AI projects",
            "Search for JavaScript frameworks and get New York weather"
        ]
        
        for i, example in enumerate(examples, 1):
            print(f"\n\nExample {i}/{len(examples)}: {example}")
            print("-" * 70)
            
            try:
                results = assistant.process_task(example)
                assistant.display_results(results)
                
                # Save each example
                with open(f"example_{i}_results.json", "w") as f:
                    json.dump(results, f, indent=2)
                    
            except Exception as e:
                print(f"Error in example {i}: {e}")
        
        print("\n" + "=" * 70)
        print("✅ ALL EXAMPLES COMPLETED")
        print("=" * 70)
        return
    
    # Interactive mode
    if args.interactive:
        print("\n🎯 INTERACTIVE MODE")
        print("=" * 70)
        print("\nI can help you with:")
        print("  • GitHub repository searches")
        print("  • Weather information")
        print("  • Combined tasks")
        print("\nExamples:")
        print("  'Find Python repositories'")
        print("  'Check weather in London'")
        print("  'Search for AI projects and get Tokyo weather'")
        print("\nType 'quit' to exit")
        print("=" * 70)
        
        while True:
            try:
                user_input = input("\n🎯 Enter task: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                if not user_input:
                    print("Please enter a task")
                    continue
                
                results = assistant.process_task(user_input)
                assistant.display_results(results)
                
                # Save results
                timestamp = int(time.time())
                filename = args.output or f"task_result_{timestamp}.json"
                with open(filename, "w") as f:
                    json.dump(results, f, indent=2)
                print(f"\n💾 Results saved to '{filename}'")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    # Single task mode
    elif args.task:
        try:
            results = assistant.process_task(args.task)
            assistant.display_results(results)
            
            # Save results
            filename = args.output or f"task_result_{int(time.time())}.json"
            with open(filename, "w") as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Results saved to '{filename}'")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)
    
    else:
        # Default demo
        print("\n📖 Running demo task...")
        demo_task = "Find AI repositories and check Tokyo weather"
        results = assistant.process_task(demo_task)
        assistant.display_results(results)
        
        print("\n" + "=" * 70)
        print("💡 TRY THESE COMMANDS:")
        print("=" * 70)
        print("  python main.py \"Search for Python projects\"")
        print("  python main.py \"What's the temperature in Paris?\"")
        print("  python main.py --interactive")
        print("  python main.py --example")
        print("=" * 70)

if __name__ == "__main__":
    run_cli()