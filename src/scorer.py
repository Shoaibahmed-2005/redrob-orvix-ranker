import datetime
from .jd_profile import (
    WEIGHTS, SKILL_CLUSTERS, PROFICIENCY_SCORE, EDUCATION_TIERS,
    RE_STRONG_POSITIVE, RE_ADJACENT, RE_HARD_NEGATIVE,
    CONSULTING_COMPANIES, RE_CS_FIELD, RE_AI_KEYWORDS
)

def _clip(val, min_v, max_v):
    return max(min_v, min(val, max_v))

def score_title_career(c):
    profile = c.get("profile", {})
    current_title = profile.get("current_title", "")
    career_history = c.get("career_history", [])
    
    titles = [exp.get("title", "") for exp in career_history]
    if current_title:
        titles.insert(0, current_title)
    latest_title = titles[0] if titles else ""
    
    base = 0.3
    if RE_STRONG_POSITIVE.search(latest_title):
        base = 0.8
    elif RE_HARD_NEGATIVE.search(latest_title):
        base = 0.1
    elif RE_ADJACENT.search(latest_title):
        all_desc = " ".join([exp.get("description", "") for exp in career_history])
        if RE_AI_KEYWORDS.search(all_desc):
            base = 0.6
        else:
            base = 0.4
            
    has_consulting = False
    has_product = False
    for exp in career_history:
        comp = exp.get("company", "").strip().lower()
        if comp in CONSULTING_COMPANIES:
            has_consulting = True
        else:
            has_product = True
            
    if has_consulting and not has_product:
        base *= 0.5
    if has_product:
        base += 0.15
        
    if len(career_history) >= 2:
        recent_desc = career_history[0].get("description", "")
        older_desc = " ".join([exp.get("description", "") for exp in career_history[1:]])
        recent_matches = len(RE_AI_KEYWORDS.findall(recent_desc))
        older_matches = len(RE_AI_KEYWORDS.findall(older_desc)) / max(1, len(career_history) - 1)
        if recent_matches > older_matches and recent_matches > 0:
            base += 0.10
            
    return _clip(base, 0.0, 1.0)

def score_skills(c):
    skills_list = c.get("skills", [])
    career_desc = " ".join([exp.get("description", "") for exp in c.get("career_history", [])]).lower()
    signals = c.get("redrob_signals", {})
    assessments = signals.get("skill_assessment_scores", {})
    
    skill_lookup = {}
    for s in skills_list:
        skill_lookup[s.get("name", "").lower()] = s

    total_score = 0.0
    for cluster_name, cluster_data in SKILL_CLUSTERS.items():
        weight = cluster_data["weight"]
        terms = cluster_data["terms"]
        
        cluster_score = 0.0
        for term in terms:
            term_score = 0.0
            if term in skill_lookup:
                s = skill_lookup[term]
                prof = PROFICIENCY_SCORE.get(s.get("proficiency"), 0.3)
                dur = s.get("duration_months", 0)
                endorse = s.get("endorsements", 0)
                
                trust_score = prof * min(1.0, dur / 36.0)
                endorse_bonus = min(0.15, (endorse / 50.0) * 0.15)
                
                # Check for assessment scores (exact or term)
                ass_score = assessments.get(s.get("name"), assessments.get(term, 0))
                assessment_bonus = (ass_score / 100.0) * 0.2
                
                term_score = trust_score + endorse_bonus + assessment_bonus
            elif career_desc.count(term) >= 2:
                term_score = 0.25
                
            cluster_score += term_score
            
        cluster_score = min(1.0, cluster_score)
        total_score += cluster_score * weight
        
    return _clip(total_score, 0.0, 1.0)

def score_experience(c):
    yoe = c.get("profile", {}).get("years_of_experience", 0)
    if yoe < 3:
        return 0.10
    elif 3 <= yoe < 5:
        return 0.50 + ((yoe - 3) / 2.0) * 0.30
    elif 5 <= yoe < 9:
        return 1.00
    elif 9 <= yoe < 12:
        return 0.85
    else:
        return 0.70

def score_location(c):
    prof = c.get("profile", {})
    loc = prof.get("location", "").lower()
    country = prof.get("country", "").lower()
    signals = c.get("redrob_signals", {})
    relocate = signals.get("willing_to_relocate", False)
    
    in_india = ("india" in country) or ("india" in loc)
    preferred_cities = {"pune", "noida", "delhi", "gurgaon", "hyderabad", "mumbai", "bangalore"}
    in_preferred = any(city in loc for city in preferred_cities)
    
    if in_india or in_preferred:
        if in_preferred:
            return 1.0
        elif relocate:
            return 0.85
        else:
            return 0.65
    else:
        if relocate:
            return 0.45
        else:
            return 0.15

def score_education(c):
    edu_list = c.get("education", [])
    if not edu_list:
        return EDUCATION_TIERS["unknown"]
        
    best_tier_score = 0.0
    field_bonus = 0.0
    
    for edu in edu_list:
        tier_str = edu.get("tier", "unknown")
        score = EDUCATION_TIERS.get(tier_str, 0.45)
        if score > best_tier_score:
            best_tier_score = score
            
        field = edu.get("field_of_study", "")
        if RE_CS_FIELD.search(field):
            field_bonus = 0.10
            
    return _clip(best_tier_score + field_bonus, 0.0, 1.0)

def score_github_oss(c):
    signals = c.get("redrob_signals", {})
    gh_score = signals.get("github_activity_score", -1)
    
    if gh_score >= 0:
        return gh_score / 100.0
        
    career_desc = " ".join([exp.get("description", "") for exp in c.get("career_history", [])]).lower()
    summary = c.get("profile", {}).get("summary", "").lower()
    full_text = career_desc + " " + summary
    
    if "open source" in full_text or "contributor" in full_text or "maintainer" in full_text:
        return 0.50
    return 0.20

def get_base_score(c):
    scores = {
        "title_career": score_title_career(c),
        "skills": score_skills(c),
        "experience": score_experience(c),
        "location": score_location(c),
        "education": score_education(c),
        "github_oss": score_github_oss(c)
    }
    final_base = sum(scores[k] * WEIGHTS[k] for k in WEIGHTS)
    return final_base, scores

def get_behavioral_multiplier(c):
    signals = c.get("redrob_signals", {})
    mult = 1.0
    
    if signals.get("open_to_work_flag"):
        mult *= 1.15
    else:
        mult *= 0.80
        
    last_active = signals.get("last_active_date")
    if last_active:
        try:
            ref = datetime.datetime(2026, 6, 28)
            la = datetime.datetime.strptime(last_active, "%Y-%m-%d")
            days_ago = (ref - la).days
            if days_ago < 30:
                mult *= 1.10
            elif 90 <= days_ago <= 180:
                mult *= 0.75
            elif days_ago > 180:
                mult *= 0.55
        except ValueError:
            pass
            
    resp_rate = signals.get("recruiter_response_rate", 0)
    if resp_rate > 0.6:
        mult *= 1.08
    elif resp_rate < 0.2:
        mult *= 0.80
        
    notice = signals.get("notice_period_days", 90)
    if notice <= 30:
        mult *= 1.10
    elif notice > 60:
        mult *= 0.88
        
    if signals.get("willing_to_relocate"):
        mult *= 1.05
        
    gh = signals.get("github_activity_score", -1)
    if gh > 50:
        mult *= 1.08
        
    icr = signals.get("interview_completion_rate", 0)
    if icr > 0.8:
        mult *= 1.05
    elif icr < 0.4:
        mult *= 0.85
        
    return mult

from .honeypot import is_honeypot

def score_candidate(c):
    if is_honeypot(c):
        return 0.0, 0.0, 1.0, {
            "title_career": 0.0, "skills": 0.0, "experience": 0.0,
            "location": 0.0, "education": 0.0, "github_oss": 0.0
        }
    base_score, breakdown = get_base_score(c)
    mult = get_behavioral_multiplier(c)
    final_score = _clip(base_score * mult, 0.0, 1.0)
    return final_score, base_score, mult, breakdown
