"""
User filtering and prioritization strategies for company analysis
"""
from typing import Dict, List, Tuple
import re

def calculate_user_priority_score(user_data: Dict) -> int:
    """
    Calculate a priority score for a user based on various signals
    Higher score = more likely to be associated with a valuable company
    """
    score = 0
    
    # 1. Has explicit company information (+50)
    if user_data.get("company"):
        score += 50
    
    # 2. Member of organizations (+30 per org, max 60)
    orgs = user_data.get("organizations", [])
    score += min(len(orgs) * 30, 60)
    
    # 3. Professional bio indicators (+20)
    bio = (user_data.get("bio") or "").lower()
    professional_keywords = ["engineer", "developer", "founder", "cto", "ceo", 
                           "lead", "manager", "architect", "data", "ml", "ai"]
    if any(keyword in bio for keyword in professional_keywords):
        score += 20
    
    # 4. Has a blog/website (+15)
    if user_data.get("blog"):
        score += 15
    
    # 5. Location indicates business hub (+10)
    location = (user_data.get("location") or "").lower()
    tech_hubs = ["san francisco", "new york", "london", "berlin", "tokyo", 
                 "seattle", "austin", "boston", "paris", "singapore"]
    if any(hub in location for hub in tech_hubs):
        score += 10
    
    # 6. Repository activity (would need additional API calls)
    # Could add: public repos count, followers count, etc.
    
    return score

def filter_and_rank_users(users: List[Dict], max_users: int) -> List[Dict]:
    """
    Filter and rank users by their likelihood of being associated with target companies
    """
    # Calculate scores
    scored_users = []
    for user in users:
        score = calculate_user_priority_score(user)
        scored_users.append((score, user))
    
    # Sort by score (highest first)
    scored_users.sort(key=lambda x: x[0], reverse=True)
    
    # Return top N users
    return [user for score, user in scored_users[:max_users]]

def is_likely_individual_account(user_data: Dict) -> bool:
    """
    Heuristics to identify likely individual/hobby accounts to skip
    """
    username = user_data.get("username", "").lower()
    bio = (user_data.get("bio") or "").lower()
    
    # Skip if username suggests individual
    individual_patterns = [
        r'^\d+$',  # Just numbers
        r'test',   # Test accounts
        r'demo',   # Demo accounts
        r'student', # Student accounts
    ]
    
    for pattern in individual_patterns:
        if re.search(pattern, username):
            return True
    
    # Skip if bio suggests individual/hobby
    hobby_keywords = ["hobby", "personal", "student", "learning", "beginner"]
    if any(keyword in bio for keyword in hobby_keywords):
        return True
    
    return False

def extract_company_signals(user_data: Dict) -> Dict:
    """
    Extract additional signals about potential company from user data
    """
    signals = {
        "confidence": "low",
        "company_type": "unknown",
        "size_hint": "unknown"
    }
    
    company = user_data.get("company", "")
    bio = user_data.get("bio", "")
    
    # Confidence based on data quality
    if company and len(company) > 3:
        signals["confidence"] = "high"
    elif user_data.get("organizations"):
        signals["confidence"] = "medium"
    
    # Company type hints
    if any(keyword in company.lower() for keyword in ["inc", "corp", "ltd", "gmbh"]):
        signals["company_type"] = "corporation"
    elif any(keyword in bio.lower() for keyword in ["startup", "founder"]):
        signals["company_type"] = "startup"
    
    # Size hints from bio
    if any(keyword in bio.lower() for keyword in ["fortune 500", "enterprise"]):
        signals["size_hint"] = "large"
    elif "startup" in bio.lower():
        signals["size_hint"] = "small"
    
    return signals