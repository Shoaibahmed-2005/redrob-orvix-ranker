import argparse
import json
import csv
import sys
import time

from src.honeypot import is_honeypot
from src.scorer import score_candidate
from src.output import generate_reasoning

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--out", default="team_Orvix.csv")
    parser.add_argument("--team-id", default="Orvix")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    
    scored_candidates = []
    honeypot_count = 0
    total = 0
    
    open_func = open
    if args.candidates.endswith(".gz"):
        import gzip
        open_func = gzip.open
        
    start_time = time.time()
    
    with open_func(args.candidates, 'rt', encoding='utf-8') as f:
        for line in f:
            total += 1
            c = json.loads(line)
            
            if is_honeypot(c):
                honeypot_count += 1
                continue
                
            final_score, base, mult, breakdown = score_candidate(c)
            scored_candidates.append({
                "candidate_id": c["candidate_id"],
                "score": final_score,
                "candidate": c,
                "breakdown": breakdown
            })
            
    # Tie-break rule: sort score descending, then candidate_id ascending
    scored_candidates.sort(key=lambda x: (-x["score"], x["candidate_id"]))
    
    top_100 = scored_candidates[:100]
    
    with open(args.out, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        
        for i, sc in enumerate(top_100):
            rank = i + 1
            reasoning = generate_reasoning(sc["candidate"], rank, sc["score"], sc["breakdown"])
            writer.writerow([sc["candidate_id"], rank, f"{sc['score']:.4f}", reasoning])
            
            if args.verbose and i < 10:
                print(f"Rank {rank}: {sc['candidate_id']} | Score: {sc['score']:.4f}")
                print(f"  Reasoning: {reasoning}")
                print(f"  Breakdown: {sc['breakdown']}")
                
    try:
        import pandas as pd
        df = pd.read_csv(args.out)
        xlsx_out = args.out.replace('.csv', '.xlsx')
        if not xlsx_out.endswith('.xlsx'):
            xlsx_out += '.xlsx'
        df.to_excel(xlsx_out, index=False)
        print(f"Top 100 written to {args.out} and {xlsx_out}")
    except ImportError:
        print(f"Top 100 written to {args.out} (Install pandas & openpyxl for XLSX output)")
        
    print(f"Total candidates scored: {total}")
    print(f"Total runtime: {time.time() - start_time:.2f}s")

if __name__ == "__main__":
    run()
