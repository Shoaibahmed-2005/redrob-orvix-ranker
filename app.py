import streamlit as st
import json
import pandas as pd

# Import our custom scoring and honeypot logic
from src.honeypot import is_honeypot
from src.scorer import score_candidate
from src.output import generate_reasoning

st.set_page_config(page_title="Orvix Candidate Ranker", layout="wide")

st.title("🏆 Orvix Candidate Ranker Sandbox")
st.markdown("Upload a JSON or JSONL candidate file to see the ranking logic in action. Honeypots will be automatically discarded, and valid profiles will be evaluated across 6 structural metrics and adjusted by a behavioral multiplier.")

uploaded_file = st.file_uploader("Upload Candidates (JSON or JSONL)", type=["json", "jsonl"])

if uploaded_file is not None:
    candidates = []
    
    try:
        content = uploaded_file.getvalue().decode("utf-8")
        if uploaded_file.name.endswith(".jsonl"):
            candidates = [json.loads(line) for line in content.strip().split('\n') if line.strip()]
        else:
            candidates = json.loads(content)
    except Exception as e:
        st.error(f"Error parsing file: {e}")
        st.stop()
        
    if not isinstance(candidates, list):
        st.error("Uploaded JSON must be a list of candidate objects, or a valid JSONL file.")
        st.stop()
        
    st.info(f"Loaded {len(candidates)} candidates. Running processing pipeline...")
    
    scored_candidates = []
    honeypot_count = 0
    
    for c in candidates:
        # Layer 1: Honeypot Filtering
        if is_honeypot(c):
            honeypot_count += 1
            continue
            
        # Layers 2 & 3: Multi-component base scoring and behavioral multiplier
        final_score, base, mult, breakdown = score_candidate(c)
        scored_candidates.append({
            "candidate_id": c["candidate_id"],
            "score": final_score,
            "candidate": c,
            "breakdown": breakdown
        })
        
    # Sort strictly by score descending, tie-break ascending
    scored_candidates.sort(key=lambda x: (-x["score"], x["candidate_id"]))
    
    # Trim to Top 100 as per competition rules
    top_100 = scored_candidates[:100]
    
    results = []
    for i, sc in enumerate(top_100):
        rank = i + 1
        reasoning = generate_reasoning(sc["candidate"], rank, sc["score"], sc["breakdown"])
        results.append({
            "Rank": rank,
            "Candidate ID": sc["candidate_id"],
            "Score": round(sc["score"], 4),
            "Reasoning": reasoning
        })
        
    df = pd.DataFrame(results)
    
    st.success(f"Processing complete! Filtered exactly {honeypot_count} honeypots from the uploaded dataset.")
    st.markdown(f"### Top {len(df)} Candidates")
    st.dataframe(df, use_container_width=True)
