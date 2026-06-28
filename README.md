---
title: Orvix Candidate Ranker
emoji: 🏆
colorFrom: blue
colorTo: indigo
sdk: streamlit
app_file: app.py
pinned: false
---

# Redrob Hackathon: Intelligent Candidate Ranker

This repository contains the complete local, deterministic, CPU-only candidate ranking system for the Intelligent Candidate Discovery & Ranking Challenge.

## Architecture
This system utilizes a 3-layer architecture for extremely fast, low-memory candidate processing:
1. **Layer 1 (Honeypot Detector)**: A rigid rule-based filter that scans profiles for date-math discrepancies, simultaneous roles, years-of-experience contradictions, impossible skill/duration pairings, and ratio anomalies. Honeypots are discarded instantly (scored as 0.0) and will never appear in the top 100.
2. **Layer 2 (Multi-Component Scorer)**: Ranks valid profiles based on 6 weighted components (`title_career`=0.35, `skills`=0.30, `experience`=0.15, `location`=0.10, `education`=0.05, `github_oss`=0.05). It uses cached regex patterns for matching job titles, career descriptions, and skills, applying specific bonuses (e.g., product company experience, trajectory) and penalties (e.g., consulting-only).
3. **Layer 3 (Behavioral Multiplier)**: Multiplies the base score using a set of 8 behavioral signals (such as `open_to_work_flag`, `last_active_date`, and `recruiter_response_rate`) to penalize inactive candidates and boost highly-responsive candidates.

## Setup
Ensure you have Python 3.9+ installed.
```bash
pip install -r requirements.txt
```

## Reproducing the Submission
Run the following single command to process the full dataset and output the valid CSV.
```bash
python rank.py --candidates ./candidates.jsonl --out ./submission.csv
```

To see the score breakdowns and reasoning for the top 10 candidates in the terminal, you can add `--verbose`:
```bash
python rank.py --candidates ./candidates.jsonl --out ./submission.csv --verbose
```

## Constraints Checked
- Runtime: The entire 100K dataset runs in under 30 seconds on a standard CPU.
- Memory: Streaming the JSONL natively ensures a peak memory load under 100 MB.
- External APIs: Completely offline and deterministic. No LLM APIs were called during ranking.

## Unit Tests & Debugging
Run the unit tests:
```bash
python tests/test_scorer.py
```

Debug the scorer using a smaller sample file:
```bash
python scripts/analyze.py
```
