def generate_reasoning(candidate, rank, score, breakdown):
    """
    Generates a 1-2 sentence deterministic reasoning string based strictly on 
    facts available in the candidate's profile and the score breakdown.
    """
    profile = candidate.get("profile", {})
    yoe = profile.get("years_of_experience", 0)
    current_title = profile.get("current_title", "Professional")
    current_company = profile.get("current_company", "a company")
    
    parts = [f"{yoe} years experienced {current_title} at {current_company}."]
    
    if breakdown["skills"] > 0.6:
        parts.append("Strong semantic match on AI/ML and retrieval skills.")
    elif breakdown["skills"] > 0.3:
        parts.append("Moderate match on required technical skills.")
    else:
        parts.append("Limited match on core AI/ML skills.")
        
    if breakdown["title_career"] > 0.6:
        parts.append("Career trajectory aligns well with product-focused AI roles.")
    elif breakdown["title_career"] < 0.3:
        parts.append("Career background shows potential misalignment with product AI focus.")
        
    signals = candidate.get("redrob_signals", {})
    if signals.get("recruiter_response_rate", 0) > 0.6:
        parts.append("High engagement signals.")
    elif signals.get("recruiter_response_rate", 1.0) < 0.2:
        parts.append("Low recruiter response rate.")
        
    if rank > 80:
        parts.append("Ranked lower due to comparative gaps, but included based on experience.")
        
    return " ".join(parts)
