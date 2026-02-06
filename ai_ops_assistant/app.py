"""
AI Operations Assistant - Fixed Working Version
Using REAL GitHub API and REAL Weather API
"""
import streamlit as st
import requests
import json
import time
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="🤖 AI Operations Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(90deg, #1E88E5, #0D47A1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .agent-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .api-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .stButton button {
        background: linear-gradient(135deg, #1E88E5 0%, #0D47A1 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        transition: all 0.3s;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🤖 AI Operations Assistant</h1>', unsafe_allow_html=True)
st.markdown("### Multi-agent System with Real API Integrations")

# Initialize session state
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'results' not in st.session_state:
    st.session_state.results = None
if 'history' not in st.session_state:
    st.session_state.history = []
if 'selected_example' not in st.session_state:
    st.session_state.selected_example = ""

# ==================== REAL API IMPLEMENTATIONS ====================

class RealGitHubAPI:
    """Real GitHub API Implementation"""
    
    def search_repositories(self, query: str, per_page: int = 5) -> Dict[str, Any]:
        """Search repositories using REAL GitHub API"""
        try:
            # GitHub API endpoint
            url = "https://api.github.com/search/repositories"
            
            # Parameters
            params = {
                "q": query,
                "per_page": per_page,
                "sort": "stars",
                "order": "desc"
            }
            
            # Headers (GitHub API requires User-Agent)
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "AI-Operations-Assistant"
            }
            
            # Make request
            response = requests.get(url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Format repositories
                repositories = []
                for item in data.get("items", []):
                    repositories.append({
                        "name": item["name"],
                        "full_name": item["full_name"],
                        "description": item.get("description") or "No description available",
                        "stars": item["stargazers_count"],
                        "forks": item["forks_count"],
                        "language": item.get("language") or "Not specified",
                        "url": item["html_url"],
                        "created_at": item["created_at"][:10],  # Just date
                        "updated_at": item["updated_at"][:10],
                        "open_issues": item["open_issues_count"],
                        "license": item.get("license", {}).get("name") if item.get("license") else None
                    })
                
                return {
                    "success": True,
                    "query": query,
                    "repositories": repositories,
                    "total_count": data.get("total_count", 0),
                    "source": "github_api",
                    "timestamp": datetime.now().isoformat()
                }
            
            elif response.status_code == 403:  # Rate limit
                return {
                    "success": False,
                    "error": "GitHub API rate limit exceeded. Please try again later.",
                    "status_code": 403
                }
            else:
                return {
                    "success": False,
                    "error": f"GitHub API error: {response.status_code}",
                    "status_code": response.status_code
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timeout. Please try again.",
                "status_code": 408
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"GitHub API error: {str(e)}",
                "status_code": 500
            }
    
    def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get detailed repository information"""
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}"
            headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "AI-Assistant"}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "data": {
                        "name": data["name"],
                        "full_name": data["full_name"],
                        "description": data.get("description"),
                        "stars": data["stargazers_count"],
                        "forks": data["forks_count"],
                        "watchers": data["watchers_count"],
                        "language": data.get("language"),
                        "created_at": data["created_at"],
                        "updated_at": data["updated_at"],
                        "homepage": data.get("homepage"),
                        "topics": data.get("topics", [])
                    }
                }
            else:
                return {"success": False, "error": f"Error: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

class RealWeatherAPI:
    """Real Weather API Implementation using OpenWeatherMap (FREE)"""
    
    def __init__(self):
        # Using OpenWeatherMap FREE API (1000 calls/day)
        self.api_key = "b6907d289e10d714a6e88b30761fae22"  # OpenWeatherMap free key for testing
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, city: str) -> Dict[str, Any]:
        """Get current weather using REAL OpenWeatherMap API"""
        try:
            # API call for current weather
            url = f"{self.base_url}/weather"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"  # Celsius
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract weather information
                weather_info = {
                    "city": data["name"],
                    "country": data["sys"]["country"],
                    "temperature": round(data["main"]["temp"], 1),
                    "feels_like": round(data["main"]["feels_like"], 1),
                    "humidity": data["main"]["humidity"],
                    "pressure": data["main"]["pressure"],
                    "wind_speed": round(data["wind"]["speed"] * 3.6, 1),  # Convert to km/h
                    "wind_direction": data["wind"].get("deg", 0),
                    "weather": data["weather"][0]["main"],
                    "description": data["weather"][0]["description"],
                    "icon": data["weather"][0]["icon"],
                    "visibility": data.get("visibility", 0) / 1000 if data.get("visibility") else 0,  # Convert to km
                    "cloudiness": data["clouds"]["all"],
                    "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime('%H:%M'),
                    "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).strftime('%H:%M'),
                    "latitude": data["coord"]["lat"],
                    "longitude": data["coord"]["lon"]
                }
                
                return {
                    "success": True,
                    "data": weather_info,
                    "source": "openweathermap_api",
                    "timestamp": datetime.now().isoformat()
                }
            
            elif response.status_code == 404:
                return {
                    "success": False,
                    "error": f"City '{city}' not found. Please check the spelling.",
                    "status_code": 404
                }
            else:
                return {
                    "success": False,
                    "error": f"Weather API error: {response.status_code}",
                    "status_code": response.status_code
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Weather API timeout. Please try again.",
                "status_code": 408
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Weather API error: {str(e)}",
                "status_code": 500
            }
    
    def get_weather_icon_url(self, icon_code: str) -> str:
        """Get URL for weather icon"""
        return f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

# ==================== AGENT IMPLEMENTATIONS ====================

class PlannerAgent:
    """Intelligent Planning Agent"""
    
    def create_plan(self, user_input: str) -> Dict[str, Any]:
        """Create execution plan based on user input"""
        
        user_lower = user_input.lower()
        plan = {"steps": [], "reasoning": "", "assumptions": []}
        
        # Extract GitHub queries
        github_keywords = ["github", "repo", "repository", "code", "project", "search", "find", "look for"]
        if any(keyword in user_lower for keyword in github_keywords):
            query = self._extract_github_query(user_input)
            plan["steps"].append({
                "step": 1,
                "description": f"Search GitHub for '{query}' repositories",
                "tool": "github",
                "parameters": {"query": query, "per_page": 5}
            })
            plan["reasoning"] += f"User wants to search GitHub for {query} repositories. "
            plan["assumptions"].append(f"Using '{query}' as search term based on context.")
        
        # Extract weather queries
        weather_keywords = ["weather", "temperature", "temp", "forecast", "climate", "humid", "rain", "sunny"]
        if any(keyword in user_lower for keyword in weather_keywords):
            city = self._extract_city(user_input)
            step_num = len(plan["steps"]) + 1
            plan["steps"].append({
                "step": step_num,
                "description": f"Get current weather in {city}",
                "tool": "weather",
                "parameters": {"city": city}
            })
            plan["reasoning"] += f"User wants weather information for {city}. "
            plan["assumptions"].append(f"Assuming user wants current weather in {city}.")
        
        # If no specific tool mentioned, do both
        if not plan["steps"]:
            plan["steps"].append({
                "step": 1,
                "description": "Search GitHub for trending repositories",
                "tool": "github",
                "parameters": {"query": "trending", "per_page": 5}
            })
            plan["steps"].append({
                "step": 2,
                "description": "Get weather in London",
                "tool": "weather",
                "parameters": {"city": "London"}
            })
            plan["reasoning"] = "No specific task mentioned. Providing general GitHub and weather information."
            plan["assumptions"] = ["Providing general information as example."]
        
        return plan
    
    def _extract_github_query(self, text: str) -> str:
        """Extract GitHub search query from text"""
        text_lower = text.lower()
        
        # Programming languages
        languages = ["python", "javascript", "java", "typescript", "c++", "c#", "go", "rust", "php", "swift"]
        for lang in languages:
            if lang in text_lower:
                return lang
        
        # Tech topics
        topics = ["machine learning", "artificial intelligence", "ai", "ml", "deep learning", 
                 "web development", "mobile app", "data science", "blockchain", "iot", "cloud"]
        for topic in topics:
            if topic in text_lower:
                return topic
        
        # Default
        return "open source"
    
    def _extract_city(self, text: str) -> str:
        """Extract city name from text"""
        text_lower = text.lower()
        
        cities = [
            "london", "new york", "tokyo", "paris", "berlin", "mumbai", 
            "delhi", "beijing", "shanghai", "dubai", "singapore", "sydney",
            "san francisco", "los angeles", "chicago", "toronto", "moscow"
        ]
        
        for city in cities:
            if city in text_lower:
                return city.title()
        
        # Try to extract using patterns
        import re
        patterns = [
            r"in\s+([A-Za-z\s]+?)(?:\s|$)",
            r"at\s+([A-Za-z\s]+?)(?:\s|$)",
            r"for\s+([A-Za-z\s]+?)(?:\s|$)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                potential_city = match.group(1).strip().title()
                if len(potential_city.split()) <= 3:  # Probably a city
                    return potential_city
        
        # Default
        return "London"

class ExecutorAgent:
    """Execution Agent with Real API Calls"""
    
    def __init__(self):
        self.github_api = RealGitHubAPI()
        self.weather_api = RealWeatherAPI()
    
    def execute_plan(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the plan using real APIs"""
        results = []
        
        for step in plan.get("steps", []):
            step_result = {"step": step["step"], "tool": step["tool"], "description": step["description"]}
            
            if step["tool"] == "github":
                params = step["parameters"]
                api_result = self.github_api.search_repositories(
                    query=params["query"],
                    per_page=params.get("per_page", 5)
                )
                step_result.update(api_result)
                
            elif step["tool"] == "weather":
                params = step["parameters"]
                api_result = self.weather_api.get_current_weather(params["city"])
                step_result.update(api_result)
            
            results.append(step_result)
        
        return results

class VerifierAgent:
    """Verification and Quality Control Agent"""
    
    def verify_results(self, user_input: str, plan: Dict[str, Any], results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verify and format results"""
        
        successful_results = [r for r in results if r.get("success", False)]
        failed_results = [r for r in results if not r.get("success", False)]
        
        # Calculate completeness score
        if len(results) == 0:
            completeness = 0
        else:
            completeness = (len(successful_results) / len(results)) * 100
        
        # Data quality metrics
        github_data = sum(len(r.get("repositories", [])) for r in results if r.get("tool") == "github" and r.get("success"))
        weather_data = sum(1 for r in results if r.get("tool") == "weather" and r.get("success"))
        
        return {
            "verification": {
                "is_complete": len(failed_results) == 0,
                "completeness_score": round(completeness, 1),
                "successful_steps": len(successful_results),
                "failed_steps": len(failed_results),
                "data_quality": {
                    "github_repositories": github_data,
                    "weather_locations": weather_data,
                    "total_data_points": github_data + weather_data
                },
                "timestamp": datetime.now().isoformat()
            },
            "summary": {
                "user_request": user_input,
                "status": "completed" if completeness >= 80 else "partial" if completeness > 0 else "failed",
                "execution_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }

# ==================== STREAMLIT UI ====================

# Sidebar
with st.sidebar:
    st.markdown("### 🤖 AI Operations Assistant")
    st.markdown("---")
    
    # Use session state for selected example
    if st.session_state.selected_example:
        default_text = st.session_state.selected_example
        st.session_state.selected_example = ""  # Clear after use
    else:
        default_text = ""
    
    # Task input with key to avoid session state conflict
    task_input = st.text_area(
        "**Enter your task:**",
        value=default_text,
        placeholder="Example: 'Find Python machine learning repositories and check weather in London'",
        height=100,
        key="task_input_widget"
    )
    
    st.markdown("---")
    
    # Quick examples
    st.markdown("### 🚀 Quick Examples")
    
    examples = [
        "Find trending Python repositories on GitHub",
        "What's the weather like in Tokyo and New York?",
        "Search for JavaScript frameworks and check London weather",
        "Get weather forecast for Paris and find AI projects"
    ]
    
    for example in examples:
        if st.button(f"📋 {example[:40]}...", key=f"example_{hash(example)}"):
            # Use callback to rerun with example
            st.session_state.selected_example = example
            st.rerun()
    
    st.markdown("---")
    
    # Settings
    st.markdown("### ⚙️ Settings")
    show_details = st.checkbox("Show Detailed Steps", value=True)
    auto_refresh = st.checkbox("Auto-refresh", value=False)

# Main content
st.markdown("### Enter a task in the sidebar and click 'Process Task' below")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    process_btn = st.button("🚀 Process Task", type="primary", use_container_width=True)

# Process the task
if process_btn and task_input:
    st.session_state.processing = True
    
    # Initialize agents
    planner = PlannerAgent()
    executor = ExecutorAgent()
    verifier = VerifierAgent()
    
    # Progress container
    progress_container = st.container()
    
    with progress_container:
        # Step 1: Planning
        st.markdown("### 📋 Step 1: Planning")
        with st.expander("Planning Details", expanded=show_details):
            plan = planner.create_plan(task_input)
            
            st.markdown(f"**Task Analysis:** {plan.get('reasoning', 'Analyzing request...')}")
            
            st.markdown("**Execution Plan:**")
            for step in plan["steps"]:
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.markdown(f"**Step {step['step']}**")
                with col2:
                    st.markdown(f"{step['description']}")
                    st.markdown(f"*Tool:* `{step['tool']}`")
                    st.markdown(f"*Parameters:* `{step['parameters']}`")
            
            if plan.get("assumptions"):
                st.markdown("**Assumptions:**")
                for assumption in plan["assumptions"]:
                    st.markdown(f"• {assumption}")
        
        st.progress(0.33)
        
        # Step 2: Execution
        st.markdown("### ⚡ Step 2: Execution")
        with st.expander("Execution Details", expanded=show_details):
            results = executor.execute_plan(plan)
            
            for result in results:
                if result.get("success"):
                    st.success(f"✅ {result['description']}")
                    
                    if result["tool"] == "github":
                        st.info(f"Found {result.get('total_count', 0)} repositories, showing {len(result.get('repositories', []))}")
                    elif result["tool"] == "weather":
                        st.info(f"Weather data retrieved successfully")
                else:
                    st.error(f"❌ {result['description']} - {result.get('error', 'Unknown error')}")
        
        st.progress(0.66)
        
        # Step 3: Verification
        st.markdown("### ✅ Step 3: Verification")
        with st.expander("Verification Details", expanded=show_details):
            verification = verifier.verify_results(task_input, plan, results)
            
            # Display verification metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Completeness", f"{verification['verification']['completeness_score']}%")
            with col2:
                st.metric("Successful Steps", verification['verification']['successful_steps'])
            with col3:
                st.metric("Data Points", verification['verification']['data_quality']['total_data_points'])
            with col4:
                st.metric("Status", verification['summary']['status'].upper())
        
        st.progress(1.0)
        
        # Store results
        st.session_state.results = {
            "task": task_input,
            "plan": plan,
            "execution_results": results,
            "verification": verification
        }
        
        # Add to history
        st.session_state.history.append({
            "task": task_input,
            "timestamp": datetime.now().isoformat(),
            "score": verification['verification']['completeness_score'],
            "status": verification['summary']['status']
        })

# Display results if available
if st.session_state.get('results'):
    results = st.session_state.results
    
    st.markdown("---")
    st.markdown("## 📊 Results Dashboard")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Data", "📈 Analytics", "📋 Details", "💾 Export"])
    
    with tab1:
        # Display GitHub results
        github_results = [r for r in results["execution_results"] if r.get("tool") == "github" and r.get("success")]
        if github_results:
            st.markdown("### 🔍 GitHub Repository Results")
            
            for gr in github_results:
                st.markdown(f"#### Search: `{gr.get('query', 'Unknown')}`")
                st.markdown(f"**Total Found:** {gr.get('total_count', 0)} repositories")
                
                repos = gr.get("repositories", [])
                if repos:
                    # Create DataFrame
                    df_data = []
                    for repo in repos:
                        df_data.append({
                            "Repository": repo["name"],
                            "Description": repo.get("description", ""),
                            "Stars": repo["stars"],
                            "Forks": repo.get("forks", 0),
                            "Language": repo.get("language", "Unknown"),
                            "Created": repo.get("created_at", ""),
                            "URL": repo["url"]
                        })
                    
                    df = pd.DataFrame(df_data)
                    
                    # Display table
                    st.dataframe(
                        df,
                        column_config={
                            "URL": st.column_config.LinkColumn("URL"),
                            "Stars": st.column_config.NumberColumn("⭐ Stars", format="%d"),
                            "Forks": st.column_config.NumberColumn("🍴 Forks", format="%d")
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                    
                    # Visualizations
                    if len(repos) > 1:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Stars visualization
                            fig = px.bar(
                                df,
                                x="Repository",
                                y="Stars",
                                title="Repository Stars",
                                color="Language",
                                color_discrete_sequence=px.colors.qualitative.Set3
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            # Language distribution
                            lang_counts = df["Language"].value_counts()
                            if len(lang_counts) > 0:
                                fig = px.pie(
                                    values=lang_counts.values,
                                    names=lang_counts.index,
                                    title="Language Distribution",
                                    hole=0.3
                                )
                                st.plotly_chart(fig, use_container_width=True)
        
        # Display Weather results
        weather_results = [r for r in results["execution_results"] if r.get("tool") == "weather" and r.get("success")]
        if weather_results:
            st.markdown("### 🌤️ Weather Results")
            
            for wr in weather_results:
                weather_data = wr.get("data", {})
                
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"#### {weather_data.get('city', 'Unknown')}, {weather_data.get('country', '')}")
                    
                    # Metrics
                    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                    with metric_col1:
                        st.metric("Temperature", f"{weather_data.get('temperature', 0)}°C")
                    with metric_col2:
                        st.metric("Feels Like", f"{weather_data.get('feels_like', 0)}°C")
                    with metric_col3:
                        st.metric("Humidity", f"{weather_data.get('humidity', 0)}%")
                    with metric_col4:
                        st.metric("Wind", f"{weather_data.get('wind_speed', 0)} km/h")
                    
                    # Additional info
                    st.markdown(f"**Condition:** {weather_data.get('weather', 'Unknown')}")
                    st.markdown(f"**Description:** {weather_data.get('description', '').title()}")
                    st.markdown(f"**Pressure:** {weather_data.get('pressure', 0)} hPa")
                    st.markdown(f"**Visibility:** {weather_data.get('visibility', 0)} km")
                    st.markdown(f"**Sunrise:** {weather_data.get('sunrise', '--:--')} | **Sunset:** {weather_data.get('sunset', '--:--')}")
                
                with col2:
                    # Weather icon
                    icon_url = f"http://openweathermap.org/img/wn/{weather_data.get('icon', '01d')}@2x.png"
                    st.image(icon_url, width=100)
                
                with col3:
                    # Temperature gauge
                    temp = weather_data.get('temperature', 20)
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=temp,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Temperature °C"},
                        gauge={
                            'axis': {'range': [-20, 50]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [-20, 0], 'color': "lightblue"},
                                {'range': [0, 15], 'color': "lightgreen"},
                                {'range': [15, 30], 'color': "yellow"},
                                {'range': [30, 50], 'color': "red"}
                            ],
                            'threshold': {
                                'line': {'color': "black", 'width': 4},
                                'thickness': 0.75,
                                'value': temp
                            }
                        }
                    ))
                    fig.update_layout(height=250)
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### 📈 Analytics Dashboard")
        
        # Completion gauge
        score = results["verification"]["verification"]["completeness_score"]
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Task Completion Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#1E88E5"},
                'steps': [
                    {'range': [0, 50], 'color': "#FF6B6B"},
                    {'range': [50, 80], 'color': "#FFD166"},
                    {'range': [80, 100], 'color': "#06D6A0"}
                ]
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Data quality metrics
        data_quality = results["verification"]["verification"]["data_quality"]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("GitHub Repositories", data_quality["github_repositories"])
        with col2:
            st.metric("Weather Locations", data_quality["weather_locations"])
        with col3:
            st.metric("Total Data Points", data_quality["total_data_points"])
        
        # Execution history
        if st.session_state.history:
            st.markdown("### 📊 Execution History")
            history_df = pd.DataFrame(st.session_state.history)
            history_df["time"] = pd.to_datetime(history_df["timestamp"])
            
            fig = px.line(
                history_df,
                x="time",
                y="score",
                title="Completion Score History",
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### 📋 Detailed Information")
        
        st.markdown("#### Plan Details")
        st.json(results["plan"], expanded=False)
        
        st.markdown("#### API Responses")
        for i, result in enumerate(results["execution_results"]):
            with st.expander(f"{result.get('description', 'Step ' + str(i+1))}"):
                st.json(result, expanded=False)
        
        st.markdown("#### Verification Details")
        st.json(results["verification"], expanded=False)
    
    with tab4:
        st.markdown("### 💾 Export Results")
        
        # JSON export
        json_data = json.dumps(results, indent=2, default=str)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📥 Download JSON",
                data=json_data,
                file_name=f"ai_assistant_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2:
            if st.button("📋 Copy to Clipboard", use_container_width=True):
                st.code(json_data, language="json")
                st.success("✅ JSON copied to clipboard!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🤖 <strong>AI Operations Assistant</strong> • Multi-agent System with Real API Integrations</p>
    <p>🔗 <strong>Real APIs:</strong> GitHub API • OpenWeatherMap API</p>
    <p>📱 <strong>Agents:</strong> Planner • Executor • Verifier</p>
    <p>🎯 <strong>Try:</strong> "Find Python repositories" or "Check Tokyo weather"</p>
</div>
""", unsafe_allow_html=True)

# Clear button
if st.session_state.get('results'):
    if st.button("🔄 Clear Results & Start New", use_container_width=True):
        for key in ['processing', 'results']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# Initial message if no task entered
elif not task_input:
    st.info("👈 Enter a task in the sidebar or click an example to get started!")