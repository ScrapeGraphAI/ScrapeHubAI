from typing import Dict, List, Tuple
import re

def evaluate_company(company_name: str, scraped_info: str, user_info: Dict = None) -> Dict[str, any]:
    """
    Evaluate if a company is a good target for selling AI scraping infrastructure.
    Score based on: industry (data/AI/e-commerce), size (>50 employees), tech relevance.
    """
    score = 0
    reasons = []
    
    # Convert scraped info to lowercase for case-insensitive matching
    info_lower = scraped_info.lower()
    
    # Tech relevance scoring (0-40 points)
    tech_keywords = {
        "ai": 10, "artificial intelligence": 10, "machine learning": 10, "ml": 8,
        "data science": 10, "data analytics": 8, "big data": 8,
        "scraping": 15, "web scraping": 15, "data extraction": 12,
        "automation": 8, "rpa": 10, "robotic process": 10,
        "api": 5, "integration": 5, "etl": 8, "data pipeline": 10
    }
    
    tech_score = 0
    found_tech = []
    for keyword, points in tech_keywords.items():
        if keyword in info_lower:
            tech_score += points
            found_tech.append(keyword)
    
    # Cap tech score at 40
    tech_score = min(tech_score, 40)
    score += tech_score
    if found_tech:
        reasons.append(f"Uses relevant technologies: {', '.join(found_tech[:3])}")
    
    # Industry fit scoring (0-30 points)
    industry_keywords = {
        "e-commerce": 15, "retail": 12, "marketplace": 12,
        "fintech": 10, "finance": 8, "banking": 8,
        "saas": 10, "software": 8, "technology": 5,
        "analytics": 10, "intelligence": 8, "insights": 8,
        "marketing": 8, "advertising": 8, "media": 6
    }
    
    industry_score = 0
    found_industries = []
    for keyword, points in industry_keywords.items():
        if keyword in info_lower:
            industry_score += points
            found_industries.append(keyword)
    
    # Cap industry score at 30
    industry_score = min(industry_score, 30)
    score += industry_score
    if found_industries:
        reasons.append(f"Operates in relevant industries: {', '.join(found_industries[:2])}")
    
    # Company size scoring (0-20 points)
    size_patterns = [
        (r"(\d+)[\s\-,]+employees", 1),
        (r"employees?[\s:]+(\d+)", 1),
        (r"team\s+of\s+(\d+)", 1),
        (r"(\d+)\s+people", 1)
    ]
    
    company_size = 0
    for pattern, group in size_patterns:
        match = re.search(pattern, info_lower)
        if match:
            try:
                company_size = int(match.group(group).replace(",", ""))
                break
            except:
                pass
    
    if company_size > 0:
        if company_size >= 1000:
            score += 20
            reasons.append(f"Large enterprise ({company_size}+ employees)")
        elif company_size >= 200:
            score += 15
            reasons.append(f"Mid-size company ({company_size} employees)")
        elif company_size >= 50:
            score += 10
            reasons.append(f"Growing company ({company_size} employees)")
        elif company_size >= 10:
            score += 5
            reasons.append(f"Small company ({company_size} employees)")
    
    # Growth indicators (0-10 points)
    growth_keywords = ["scaling", "growing", "expanding", "hiring", "series a", "series b", 
                      "series c", "funded", "funding", "investment", "unicorn"]
    growth_found = [kw for kw in growth_keywords if kw in info_lower]
    if growth_found:
        score += 10
        reasons.append("Shows growth indicators")
    
    # Data needs indicators (bonus points)
    if any(keyword in info_lower for keyword in ["competitive intelligence", "market research", 
                                                  "price monitoring", "lead generation",
                                                  "content aggregation", "data collection"]):
        score += 10
        reasons.append("Has explicit data collection needs")
    
    # Normalize score to 0-100
    final_score = min(score, 100)
    
    # Determine recommendation
    if final_score >= 70:
        recommendation = "High Priority"
    elif final_score >= 50:
        recommendation = "Medium Priority"
    elif final_score >= 30:
        recommendation = "Low Priority"
    else:
        recommendation = "Not Recommended"
    
    return {
        "company": company_name,
        "score": final_score,
        "recommendation": recommendation,
        "reasons": reasons,
        "company_size": company_size if company_size > 0 else "Unknown",
        "summary": f"{recommendation} - " + ("; ".join(reasons) if reasons else "Limited relevant indicators found")
    }

def rank_companies(evaluations: List[Dict]) -> List[Dict]:
    """
    Rank companies by score and return sorted list.
    """
    return sorted(evaluations, key=lambda x: x["score"], reverse=True)