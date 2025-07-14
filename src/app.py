import streamlit as st
import os
import sys
from dotenv import load_dotenv
import pandas as pd

# Add the parent directory to sys.path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import run_agent

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="ScrapeHub",
    page_icon="⭐",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .company-card {
        background-color: #1e1e1e;
        color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #333;
    }
    .company-card h3 {
        color: #ffffff;
        margin-top: 0;
        margin-bottom: 10px;
    }
    .company-card p {
        color: #e0e0e0;
        margin: 5px 0;
    }
    .company-card small {
        color: #b0b0b0;
    }
    .high-priority {
        border-left: 5px solid #00cc00;
    }
    .medium-priority {
        border-left: 5px solid #ffcc00;
    }
    .low-priority {
        border-left: 5px solid #ff6666;
    }
    
    /* Light mode overrides */
    @media (prefers-color-scheme: light) {
        .company-card {
            background-color: #f0f2f6;
            color: #000000;
            border: 1px solid #ddd;
        }
        .company-card h3 {
            color: #000000;
        }
        .company-card p {
            color: #333333;
        }
        .company-card small {
            color: #666666;
        }
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🌟 ScrapeHub")
st.markdown("""
This agent analyzes GitHub stargazers from a repository, traces them to their companies, 
and evaluates these companies as potential sales targets for AI scraping infrastructure.
""")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    
    # Check API keys
    api_keys_status = {
        "GitHub Token": bool(os.getenv("GITHUB_TOKEN")),
        "OpenRouter API Key": bool(os.getenv("OPENROUTER_API_KEY")),
        "ScrapeGraphAI API Key": bool(os.getenv("SGAI_API_KEY"))
    }
    
    st.subheader("API Keys Status")
    for key, status in api_keys_status.items():
        if status:
            st.success(f"✅ {key} configured")
        else:
            st.error(f"❌ {key} missing")
    
    if not all(api_keys_status.values()):
        st.warning("Please configure all API keys in the .env file")
    
    st.markdown("---")
    
    # Advanced settings
    with st.expander("Advanced Settings"):
        max_stargazers = st.slider("Max stargazers to fetch", 100, 5000, 1000, step=100, 
                                   help="Higher values take longer but find more companies")
        max_users_to_analyze = st.slider("Max users to analyze for companies", 50, 500, 100, step=50,
                                        help="Number of stargazers to check for company info")
        max_results = st.slider("Max companies to display", 10, 50, 20)
        min_score = st.slider("Minimum score threshold", 0, 100, 30)

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    repo_input = st.text_input(
        "GitHub Repository (owner/repo)",
        value="ScrapeGraphAI/Scrapegraph-ai",
        placeholder="e.g., facebook/react",
        help="Enter the GitHub repository in the format: owner/repository"
    )

with col2:
    st.empty()
    analyze_button = st.button("🔍 Analyze Repository", type="primary", use_container_width=True)

# Results section
if analyze_button:
    if not all(api_keys_status.values()):
        st.error("Please configure all required API keys in the .env file before running the analysis.")
    elif not repo_input or "/" not in repo_input:
        st.error("Please enter a valid GitHub repository in the format: owner/repository")
    else:
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with st.spinner("Running analysis..."):
            status_text.text("Initializing agent...")
            progress_bar.progress(10)
            
            # Run the agent with configuration
            result = run_agent(repo_input, max_stargazers=max_stargazers, max_users=max_users_to_analyze)
            
            progress_bar.progress(100)
            status_text.text("Analysis complete!")
        
        # Display results
        if result["success"]:
            st.success(f"✅ Analysis completed successfully!")
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Stargazers", result["total_stargazers"])
            with col2:
                st.metric("Companies Found", result["total_companies"])
            with col3:
                high_value = len([e for e in result["evaluations"] if e["score"] >= 70])
                st.metric("High-Value Targets", high_value)
            
            # Filter evaluations
            evaluations = [e for e in result["evaluations"] if e["score"] >= min_score][:max_results]
            
            if evaluations:
                st.markdown("---")
                st.subheader("🎯 Top Company Targets")
                
                # Create tabs for different views
                tab1, tab2 = st.tabs(["Card View", "Table View"])
                
                with tab1:
                    # Card view
                    for i, eval_data in enumerate(evaluations):
                        priority_class = ""
                        if eval_data["recommendation"] == "High Priority":
                            priority_class = "high-priority"
                        elif eval_data["recommendation"] == "Medium Priority":
                            priority_class = "medium-priority"
                        else:
                            priority_class = "low-priority"
                        
                        # Create card content with proper HTML escaping
                        company_name = eval_data.get('company', 'Unknown Company')
                        score = eval_data.get('score', 0)
                        recommendation = eval_data.get('recommendation', 'Unknown')
                        company_size = eval_data.get('company_size', 'Unknown')
                        summary = eval_data.get('summary', 'No summary available')
                        source_user = eval_data.get('source_user', 'Unknown')
                        
                        # Get user info if available
                        user_info = eval_data.get('user_info', {})
                        email = user_info.get('email', '')
                        
                        card_html = f"""
                        <div class="company-card {priority_class}">
                            <h3>{i+1}. {company_name}</h3>
                            <p><strong>Score:</strong> {score}/100 | 
                               <strong>Priority:</strong> {recommendation} | 
                               <strong>Size:</strong> {company_size}</p>
                            <p><strong>Summary:</strong> {summary}</p>
                            <p><small><strong>Source:</strong> GitHub user @{source_user}</small></p>
                        """
                        
                        if email:
                            card_html += f'<p><small><strong>Contact:</strong> {email}</small></p>'
                        
                        card_html += "</div>"
                        
                        st.markdown(card_html, unsafe_allow_html=True)
                
                with tab2:
                    # Table view
                    df_data = []
                    for eval_data in evaluations:
                        user_info = eval_data.get('user_info', {})
                        email = user_info.get('email', '')
                        
                        row_data = {
                            "Company": eval_data['company'],
                            "Score": eval_data['score'],
                            "Priority": eval_data['recommendation'],
                            "Size": eval_data.get('company_size', 'Unknown'),
                            "Key Reasons": "; ".join(eval_data.get('reasons', [])[:2])
                        }
                        
                        # Add email if available
                        if email:
                            row_data["Contact Email"] = email
                            
                        df_data.append(row_data)
                    
                    df = pd.DataFrame(df_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Download button
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Results (CSV)",
                        data=csv,
                        file_name=f"{repo_input.replace('/', '_')}_analysis.csv",
                        mime="text/csv"
                    )
            else:
                st.warning("No companies found matching the criteria. Try adjusting the filters or analyzing a different repository.")
        
        else:
            st.error(f"❌ Analysis failed: {result['error']}")
            st.info("Please check your API keys and try again. Make sure the repository exists and is public.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>Built with LangGraph, ScrapeGraphAI, and Streamlit</p>
    <p>⚠️ Please respect rate limits and website terms of service when using this tool.</p>
</div>
""", unsafe_allow_html=True)