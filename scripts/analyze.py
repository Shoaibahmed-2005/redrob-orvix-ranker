import sys
import os
import json

# Add root directory to sys.path to allow importing src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.honeypot import is_honeypot
from src.scorer import score_candidate

def run_analysis(file_path):
    print(f"Analyzing {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        candidates = json.load(f)
        
    scored = []
    honeypots = 0
    for c in candidates:
        if is_honeypot(c):
            honeypots += 1
            continue
            
        final_score, base, mult, breakdown = score_candidate(c)
        scored.append((final_score, base, mult, breakdown, c))
        
    scored.sort(key=lambda x: -x[0])
    
    print(f"\nFiltered {honeypots} honeypots.")
    print(f"Top 10 candidates out of {len(scored)} valid candidates:")
    print("-" * 140)
    print(f"{'Rank':<5} | {'Candidate ID':<15} | {'Final':<6} | {'Base':<6} | {'Mult':<5} | {'Title':<5} | {'Skill':<5} | {'Exp':<4} | {'Loc':<4} | {'Edu':<4} | {'GH':<4} | {'Current Title'}")
    print("-" * 140)
    
    for i, (final_score, base, mult, b, c) in enumerate(scored[:20]):
        rank = i + 1
        cid = c["candidate_id"]
        ctitle = c.get("profile", {}).get("current_title", "")[:35]
        print(f"{rank:<5} | {cid:<15} | {final_score:.4f} | {base:.4f} | {mult:.3f} | {b['title_career']:.3f} | {b['skills']:.3f} | {b['experience']:.2f} | {b['location']:.2f} | {b['education']:.2f} | {b['github_oss']:.2f} | {ctitle}")

if __name__ == "__main__":
    run_analysis("sample_candidates.json")
