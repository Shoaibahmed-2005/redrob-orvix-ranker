import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scorer import score_candidate
from src.honeypot import is_honeypot

def create_base_candidate():
    return {
        "candidate_id": "CAND_TEST001",
        "profile": {
            "years_of_experience": 6,
            "current_title": "Software Engineer",
            "current_company": "Acme Corp",
            "location": "Pune, India",
            "country": "India"
        },
        "career_history": [
            {
                "title": "Software Engineer",
                "company": "Acme Corp",
                "start_date": "2020-01-01",
                "end_date": "2026-01-01",
                "duration_months": 72,
                "is_current": False,
                "description": "Building backend systems."
            }
        ],
        "skills": [],
        "redrob_signals": {
            "last_active_date": "2026-06-01",
            "recruiter_response_rate": 0.8,
            "notice_period_days": 30,
            "connection_count": 50,
            "endorsements_received": 10
        }
    }

def test_valid_candidate_not_honeypot():
    c = create_base_candidate()
    assert is_honeypot(c) is False
    final, _, _, _ = score_candidate(c)
    assert final > 0.0
    print("test_valid_candidate_not_honeypot passed.")

def test_honeypot_expert_skills_zero_duration():
    c = create_base_candidate()
    c["skills"] = [
        {"name": "Python", "proficiency": "expert", "duration_months": 0},
        {"name": "Java", "proficiency": "expert", "duration_months": 0},
        {"name": "C++", "proficiency": "advanced", "duration_months": 0}
    ]
    assert is_honeypot(c) is True
    final, _, _, _ = score_candidate(c)
    assert final < 0.05
    print("test_honeypot_expert_skills_zero_duration passed.")

def test_honeypot_duration_mismatch():
    c = create_base_candidate()
    c["career_history"][0]["duration_months"] = 120 # Actual gap is ~72
    assert is_honeypot(c) is True
    print("test_honeypot_duration_mismatch passed.")
    
def test_honeypot_multiple_current_jobs():
    c = create_base_candidate()
    c["career_history"].append({
        "title": "Job 2", "company": "Corp B", "start_date": "2022-01-01", 
        "end_date": None, "duration_months": 53, "is_current": True
    })
    c["career_history"].append({
        "title": "Job 3", "company": "Corp C", "start_date": "2023-01-01", 
        "end_date": None, "duration_months": 41, "is_current": True
    })
    assert is_honeypot(c) is True
    print("test_honeypot_multiple_current_jobs passed.")

def test_ai_engineer_vs_marketing_manager():
    ai = create_base_candidate()
    ai["profile"]["current_title"] = "AI Engineer"
    ai["career_history"][0]["title"] = "AI Engineer"
    
    mktg = create_base_candidate()
    mktg["profile"]["current_title"] = "Marketing Manager"
    mktg["career_history"][0]["title"] = "Marketing Manager"
    
    final_ai, base_ai, _, _ = score_candidate(ai)
    final_mktg, base_mktg, _, _ = score_candidate(mktg)
    
    assert base_ai > 0.5
    assert base_mktg < 0.4
    assert base_ai > base_mktg
    print("test_ai_engineer_vs_marketing_manager passed.")

def test_inactive_candidate_penalty():
    active = create_base_candidate()
    
    inactive = create_base_candidate()
    inactive["redrob_signals"]["last_active_date"] = "2025-01-01" # > 180 days ago
    inactive["redrob_signals"]["recruiter_response_rate"] = 0.1 # Low response rate
    
    _, _, mult_active, _ = score_candidate(active)
    _, _, mult_inactive, _ = score_candidate(inactive)
    
    assert mult_active > mult_inactive
    print("test_inactive_candidate_penalty passed.")

if __name__ == "__main__":
    test_valid_candidate_not_honeypot()
    test_honeypot_expert_skills_zero_duration()
    test_honeypot_duration_mismatch()
    test_honeypot_multiple_current_jobs()
    test_ai_engineer_vs_marketing_manager()
    test_inactive_candidate_penalty()
    print("All tests passed.")
