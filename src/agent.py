import os
import sys
from typing import TypedDict, List, Dict, Annotated, Sequence
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph.message import add_messages

# Add the parent directory to sys.path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools import fetch_stargazers, get_user_company, search_company_info
from src.evaluator import evaluate_company, rank_companies

load_dotenv()

# Configure OpenRouter as LLM
llm = ChatOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1"),
    model="openai/gpt-4o-mini",
    temperature=0.3
)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    repo: str
    stargazers: List[str]
    companies: List[Dict]
    evaluations: List[Dict]
    current_step: str
    error: str
    max_stargazers: int
    max_users: int

def fetch_stargazers_node(state: AgentState) -> AgentState:
    """Fetch GitHub stargazers for the repository."""
    try:
        print(f"Fetching stargazers for {state['repo']}...")
        max_stargazers = state.get("max_stargazers", 1000)
        result = fetch_stargazers.invoke({"repo": state["repo"], "max_stargazers": max_stargazers})
        
        # Handle the result properly
        if isinstance(result, str):
            if result.startswith("Error"):
                state["error"] = result
                state["stargazers"] = []
            else:
                state["error"] = "Unexpected string response from fetch_stargazers"
                state["stargazers"] = []
        elif isinstance(result, list):
            if result and isinstance(result[0], str) and result[0].startswith("Error"):
                state["error"] = result[0]
                state["stargazers"] = []
            else:
                state["stargazers"] = result
                print(f"Found {len(result)} stargazers")
        else:
            state["error"] = f"Unexpected response type: {type(result)}"
            state["stargazers"] = []
        
        state["current_step"] = "trace_companies"
        return state
    except Exception as e:
        state["error"] = f"Error fetching stargazers: {str(e)}"
        state["current_step"] = "end"
        return state

def trace_companies_node(state: AgentState) -> AgentState:
    """Trace stargazers to their companies."""
    try:
        companies = []
        processed_companies = set()
        
        # Limit processing to avoid rate limiting
        # You can increase this but be aware of GitHub API rate limits (5000/hour with auth)
        configured_max = state.get("max_users", 100)
        max_users = min(len(state["stargazers"]), configured_max)
        print(f"Processing {max_users} users to find companies...")
        
        for i, user in enumerate(state["stargazers"][:max_users]):
            if i % 10 == 0:
                print(f"Processing user {i+1}/{max_users}...")
            elif i < 5 or i >= max_users - 5:  # Show first 5 and last 5
                print(f"Processing user {i+1}/{max_users}...")
            
            result = get_user_company.invoke({"username": user})
            # Ensure we have a dict response
            if isinstance(result, dict):
                user_info = result
            else:
                user_info = {"username": user, "company": None, "organizations": [], "error": str(result)}
            
            # Extract company name
            company_name = None
            if user_info.get("company"):
                company_name = user_info["company"].strip()
            elif user_info.get("organizations"):
                # Use the first organization as company
                company_name = user_info["organizations"][0]
            
            # Skip if no company found or already processed
            if company_name and company_name not in processed_companies:
                processed_companies.add(company_name)
                companies.append({
                    "name": company_name,
                    "source_user": user,
                    "user_info": user_info
                })
        
        print(f"Found {len(companies)} unique companies")
        state["companies"] = companies
        state["current_step"] = "evaluate_companies"
        return state
    except Exception as e:
        state["error"] = f"Error tracing companies: {str(e)}"
        state["current_step"] = "end"
        return state

def evaluate_companies_node(state: AgentState) -> AgentState:
    """Evaluate and rank companies as sales targets."""
    try:
        evaluations = []
        
        print(f"Evaluating {len(state['companies'])} companies...")
        
        for i, company in enumerate(state["companies"]):
            if i % 5 == 0:
                print(f"Evaluating company {i+1}/{len(state['companies'])}...")
            
            # Search for company information
            try:
                company_info_result = search_company_info.invoke({
                    "company_name": company["name"]
                })
                # Ensure we have a string response
                company_info = str(company_info_result) if company_info_result else "No information found"
            except Exception as e:
                print(f"Error searching for company {company['name']}: {str(e)}")
                company_info = f"Error retrieving information: {str(e)}"
            
            # Evaluate the company
            evaluation = evaluate_company(
                company_name=company["name"],
                scraped_info=company_info,
                user_info=company.get("user_info")
            )
            
            # Add source user info
            evaluation["source_user"] = company["source_user"]
            evaluation["user_info"] = company.get("user_info", {})
            evaluations.append(evaluation)
        
        # Rank companies by score
        ranked_evaluations = rank_companies(evaluations)
        state["evaluations"] = ranked_evaluations
        state["current_step"] = "end"
        
        print(f"Evaluation complete. Found {len([e for e in ranked_evaluations if e['score'] >= 50])} high-value targets.")
        return state
    except Exception as e:
        state["error"] = f"Error evaluating companies: {str(e)}"
        state["current_step"] = "end"
        return state

def should_continue(state: AgentState) -> str:
    """Determine the next step in the workflow."""
    if state.get("error"):
        return "end"
    
    step = state.get("current_step", "fetch")
    if step == "fetch":
        return "fetch"
    elif step == "trace_companies":
        return "trace"
    elif step == "evaluate_companies":
        return "evaluate"
    else:
        return "end"

# Build the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("fetch", fetch_stargazers_node)
workflow.add_node("trace", trace_companies_node)
workflow.add_node("evaluate", evaluate_companies_node)

# Add edges
workflow.add_conditional_edges(
    "__start__",
    should_continue,
    {
        "fetch": "fetch",
        "end": END
    }
)

workflow.add_conditional_edges(
    "fetch",
    lambda x: "trace" if not x.get("error") and x.get("stargazers") else "end",
    {
        "trace": "trace",
        "end": END
    }
)

workflow.add_conditional_edges(
    "trace",
    lambda x: "evaluate" if not x.get("error") and x.get("companies") else "end",
    {
        "evaluate": "evaluate",
        "end": END
    }
)

workflow.add_edge("evaluate", END)

# Compile the graph
graph = workflow.compile()

def run_agent(repo: str, max_stargazers: int = 1000, max_users: int = 100) -> Dict:
    """Run the agent to analyze GitHub stargazers and find sales targets.
    
    Args:
        repo: GitHub repository in format "owner/repo"
        max_stargazers: Maximum number of stargazers to fetch (default: 1000)
        max_users: Maximum number of users to analyze for companies (default: 100)
    """
    initial_state = {
        "messages": [],
        "repo": repo,
        "stargazers": [],
        "companies": [],
        "evaluations": [],
        "current_step": "fetch",
        "error": None,
        "max_stargazers": max_stargazers,
        "max_users": max_users
    }
    
    try:
        result = graph.invoke(initial_state)
        return {
            "success": not bool(result.get("error")),
            "error": result.get("error"),
            "evaluations": result.get("evaluations", []),
            "total_stargazers": len(result.get("stargazers", [])),
            "total_companies": len(result.get("companies", []))
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "evaluations": [],
            "total_stargazers": 0,
            "total_companies": 0
        }