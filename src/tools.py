import os
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv
from langchain.tools import tool
from scrapegraph_py import Client

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
SGAI_API_KEY = os.getenv("SGAI_API_KEY")

if SGAI_API_KEY:
    SGAI_CLIENT = Client(api_key=SGAI_API_KEY)
else:
    SGAI_CLIENT = None

@tool
def fetch_stargazers(repo: str, max_stargazers: int = 1000) -> List[str]:
    """Fetch list of GitHub users who starred a repo (e.g., 'ScrapeGraphAI/Scrapegraph-ai')."""
    try:
        owner, repo_name = repo.split('/')
        
        # First, get the total star count
        repo_url = f"https://api.github.com/repos/{owner}/{repo_name}"
        repo_response = requests.get(repo_url, headers=HEADERS)
        repo_response.raise_for_status()
        total_stars = repo_response.json().get('stargazers_count', 0)
        print(f"Repository has {total_stars:,} total stars")
        
        url = f"https://api.github.com/repos/{owner}/{repo_name}/stargazers"
        
        stargazers = []
        page = 1
        while True:
            response = requests.get(url, headers=HEADERS, params={"per_page": 100, "page": page})
            response.raise_for_status()
            
            # Check rate limit
            remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
            if remaining < 10:
                print(f"Warning: GitHub API rate limit low ({remaining} requests remaining)")
            
            data = response.json()
            if not data:
                break
            stargazers.extend([user['login'] for user in data])
            
            print(f"Fetched {len(stargazers):,} stargazers so far...")
            
            page += 1
            # Configurable limit to avoid rate limiting
            if len(stargazers) >= max_stargazers:
                print(f"Reached configured limit of {max_stargazers:,} stargazers")
                break
        
        print(f"Total stargazers fetched: {len(stargazers):,}")
        return stargazers
    except Exception as e:
        return [f"Error fetching stargazers: {str(e)}"]

@tool
def get_user_company(username: str) -> Dict[str, any]:
    """Get company and orgs for a GitHub user."""
    try:
        user_url = f"https://api.github.com/users/{username}"
        orgs_url = f"https://api.github.com/users/{username}/orgs"
        
        user_response = requests.get(user_url, headers=HEADERS)
        user_response.raise_for_status()
        user_data = user_response.json()
        
        orgs_response = requests.get(orgs_url, headers=HEADERS)
        orgs_response.raise_for_status()
        orgs_data = orgs_response.json()
        
        return {
            "username": username,
            "company": user_data.get("company"),
            "organizations": [org['login'] for org in orgs_data],
            "name": user_data.get("name"),
            "bio": user_data.get("bio"),
            "location": user_data.get("location"),
            "blog": user_data.get("blog"),
            "email": user_data.get("email"),  # Public email if available
            "twitter_username": user_data.get("twitter_username"),
            "followers": user_data.get("followers", 0),
            "following": user_data.get("following", 0),
            "public_repos": user_data.get("public_repos", 0)
        }
    except Exception as e:
        return {
            "username": username,
            "company": None,
            "organizations": [],
            "error": str(e)
        }

@tool
def scrape_webpage(url: str, prompt: str) -> str:
    """Use ScrapeGraphAI API (smartscraper endpoint) to scrape and extract data from a webpage with a custom prompt."""
    if not SGAI_CLIENT:
        return "Error: ScrapeGraphAI API key not configured"
    
    try:
        # Use the smartscraper endpoint
        response = SGAI_CLIENT.smartscraper(
            website_url=url,
            user_prompt=prompt
        )
        
        # Extract result from response
        if isinstance(response, dict):
            result = response.get('result', response)
            if isinstance(result, dict):
                return str(result)
            return str(result)
        return str(response)
    except Exception as e:
        return f"Error using ScrapeGraphAI API: {str(e)}"

@tool
def search_company_web(company_name: str) -> Dict[str, any]:
    """Search for company information using ScrapeGraphAI's searchscraper."""
    if not SGAI_CLIENT:
        return {"error": "ScrapeGraphAI API key not configured"}
    
    try:
        # Use searchscraper to find comprehensive company information
        search_prompt = f"""Find comprehensive information about {company_name} company:
        - Official website URL
        - Company size (number of employees)
        - Industry and sector
        - Main products or services
        - Technology stack or technical focus
        - Whether they work with AI, data, or e-commerce
        - Recent news or developments
        - Headquarters location
        """
        
        response = SGAI_CLIENT.searchscraper(
            user_prompt=search_prompt
        )
        
        if isinstance(response, dict):
            result = response.get('result', '')
            urls = response.get('reference_urls', [])
            
            # Try to find the official website from reference URLs
            official_url = ""
            for url in urls:
                if company_name.lower().replace(' ', '') in url.lower():
                    if not any(skip in url for skip in ['wikipedia', 'crunchbase', 'facebook', 'twitter', 'news']):
                        official_url = url
                        break
                elif 'linkedin.com/company' in url and company_name.lower() in url.lower():
                    official_url = url  # LinkedIn is good fallback
            
            return {
                "info": str(result),
                "official_url": official_url,
                "sources": urls
            }
        
        return {"error": "No results found"}
    except Exception as e:
        print(f"Error using searchscraper: {str(e)}")
        return {"error": str(e)}

@tool
def search_company_info(company_name: str) -> str:
    """Search for company information using web search and scraping."""
    if not company_name:
        return "No company name provided"
    
    # Clean company name (remove @ symbol if present)
    company_name = company_name.strip().lstrip('@')
    
    # First, use searchscraper to find comprehensive information
    print(f"Searching web for information about {company_name}...")
    search_result = search_company_web.invoke({"company_name": company_name})
    
    if isinstance(search_result, dict) and not search_result.get("error"):
        # We got good information from search
        info = search_result.get("info", "")
        official_url = search_result.get("official_url", "")
        
        # If we have enough information from search, return it
        if info and len(info) > 100:  # Reasonable amount of info
            print(f"Found comprehensive information via web search")
            return info
        
        # If we have an official URL, try to scrape it for more details
        if official_url:
            print(f"Found official URL: {official_url}, scraping for more details...")
            detailed_prompt = f"""Extract detailed information about {company_name}:
            - Company size (exact number of employees if available)
            - Industry and sector classification
            - Complete list of main products or services
            - Technology stack and technical infrastructure
            - AI, machine learning, or data processing capabilities
            - Data analytics or business intelligence needs
            - Target customers and market segments
            - Recent developments or growth indicators
            """
            
            scrape_result = scrape_webpage.invoke({"url": official_url, "prompt": detailed_prompt})
            if scrape_result and "Error" not in str(scrape_result):
                # Combine search info with scraped details
                combined_info = f"Search Results:\n{info}\n\nDetailed Information from {official_url}:\n{scrape_result}"
                return combined_info
    
    # Fallback: Try LinkedIn directly if search didn't work well
    linkedin_url = f"https://www.linkedin.com/company/{company_name.lower().replace(' ', '-')}"
    print(f"Trying LinkedIn as fallback: {linkedin_url}")
    
    linkedin_prompt = f"""Extract information about {company_name}:
    - Company size (number of employees)
    - Industry and sector
    - Main products or services
    - Technology focus
    - Business description
    """
    
    linkedin_result = scrape_webpage.invoke({"url": linkedin_url, "prompt": linkedin_prompt})
    if linkedin_result and "Error" not in str(linkedin_result):
        return f"LinkedIn Information:\n{linkedin_result}"
    
    # If we got some info from search but not much, return it
    if isinstance(search_result, dict) and search_result.get("info"):
        return search_result["info"]
    
    return f"Could not find detailed information for {company_name}"