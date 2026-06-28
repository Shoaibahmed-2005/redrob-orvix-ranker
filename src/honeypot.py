from datetime import datetime

# The reference date used for evaluating 'current' jobs and dates
REFERENCE_DATE = datetime(2026, 6, 28)

def is_honeypot(c):
    """
    Evaluates a candidate profile against 6 honeypot rules.
    Returns True if the candidate is a honeypot, False otherwise.
    """
    # 1. Expert/advanced skills listed with 0 months duration (3+ = honeypot)
    skills_0_months = sum(
        1 for s in c.get("skills", [])
        if s.get("proficiency") in ["advanced", "expert"] and s.get("duration_months", 0) == 0
    )
    if skills_0_months >= 3:
        return True
                
    # 2. Career history date math (15 month slack for open, 3 month slack for closed)
    for exp in c.get("career_history", []):
        start_str = exp.get("start_date")
        end_str = exp.get("end_date")
        stated_months = exp.get("duration_months", 0)
        
        if not start_str: 
            continue
            
        try:
            start_dt = datetime.strptime(start_str, "%Y-%m-%d")
            is_open = False
            if end_str:
                end_dt = datetime.strptime(end_str, "%Y-%m-%d")
            else:
                end_dt = REFERENCE_DATE
                is_open = True
            
            actual_months = (end_dt - start_dt).days / 30.437
            diff = abs(actual_months - stated_months)
            
            if is_open and diff > 15:
                return True
            if not is_open and diff > 3:
                return True
        except ValueError:
            pass
            
    # 3. Multiple is_current=true jobs simultaneously
    current_jobs = sum(1 for exp in c.get("career_history", []) if exp.get("is_current"))
    if current_jobs > 1:
        return True
        
    # 4. years_of_experience discrepancy (> 5 years)
    profile_yoe = c.get("profile", {}).get("years_of_experience", 0)
    sum_career_months = sum(exp.get("duration_months", 0) for exp in c.get("career_history", []))
    if abs(profile_yoe - (sum_career_months / 12.0)) > 5.0:
        return True
        
    # 5. Endorsements/connections ratio anomalies (e.g. 500 endorsements, 3 connections)
    signals = c.get("redrob_signals", {})
    connections = signals.get("connection_count", 0)
    endorsements = signals.get("endorsements_received", 0)
    
    if connections > 0 and (endorsements / connections) >= 100.0:
        return True
    if connections == 0 and endorsements > 100:
        return True
        
    # 6. Uniform expert proficiency across 85%+ of a large skill list
    skills = c.get("skills", [])
    if len(skills) >= 10:
        expert_count = sum(1 for s in skills if s.get("proficiency") == "expert")
        if (expert_count / len(skills)) >= 0.85:
            return True
            
    return False
