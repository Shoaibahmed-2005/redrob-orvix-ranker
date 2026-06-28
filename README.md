---
title: Orvix Candidate Ranker
emoji: 🏆
colorFrom: blue
colorTo: indigo
sdk: streamlit
app_file: app.py
pinned: false
---

# 🏆 Team Orvix: Intelligent Candidate Discovery & Ranking

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Status: Complete](https://img.shields.io/badge/Status-Complete-success.svg)]()

> **Redrob Hackathon** submission for building a deterministic, offline, and high-performance candidate ranking engine.

## 📖 Overview

This project is an algorithmic candidate evaluation system designed to act as an AI recruiter. It processes large-scale, synthetic candidate datasets (up to 100,000 profiles), evaluates them against a Senior AI Engineer job description, and identifies the **Top 100** best-fit candidates while strictly enforcing logical integrity (catching fabricated "honeypot" profiles).

---

## 🏗️ System Architecture

The solution uses a highly optimized streaming architecture divided into **3 distinct functional layers** built natively in Python. It avoids heavy API calls to ensure it runs entirely locally and deterministically.

### Layer 1: The Honeypot Detector
A rigid rule-based filter that scans profiles for impossible states to discard fabricated resumes.
- Scans for **duration mismatches** (e.g. 10 years of experience claimed, but jobs only sum to 2 years).
- Catches impossible **skill claims** (e.g. "Expert" proficiency logged with 0 months of actual use).
- Flags anomalous connections-to-endorsements ratios.

### Layer 2: Multi-Component Base Scorer
Scores valid profiles dynamically across 6 heavily-weighted domains:
1. **Title & Career Trajectory (35%)**: Prioritizes Product AI Engineers over Consulting/Marketing roles.
2. **Technical Skills (30%)**: Matches 5 vectors (Embeddings, Vector DBs, Ranking, LLM/NLP, Python/ML) weighted by months of experience and proficiency.
3. **Experience (15%)**: Scales based on the optimal 5-9 year sweet spot.
4. **Location (10%)**: Checks for Indian cities or willingness to relocate.
5. **Education (5%)** & **GitHub Open Source Activity (5%)**.

### Layer 3: Behavioral Multiplier
Acts as the final modifier, scaling the base score depending on platform engagement metrics (e.g., `last_active_date`, `recruiter_response_rate`, `open_to_work_flag`).

---

## 🚀 Performance Metrics
The system operates well within the rigid Hackathon constraints:
- **Compute:** Evaluates **100,000 records in ~28 seconds** (Constraint: < 5 mins) on a standard CPU.
- **Memory:** Utilizes Native Python streaming iterators, maintaining a peak memory footprint of `< 100 MB` (Constraint: < 16GB).
- **Network:** 100% offline parsing. No LLMs or third-party APIs are called during execution.

---

## 💻 How to Run Locally

### 1. Install Dependencies
Ensure you are using a Python virtual environment, then run:
```bash
pip install -r requirements.txt
```

### 2. Generate the Top 100 Submission
To process the full dataset and generate the final output files:
```bash
python rank.py --candidates ./candidates.jsonl
```
*This will output exactly 100 rows into `team_Orvix.csv` and `team_Orvix.xlsx`.*

### 3. Run the Sandbox Web UI
To visualize the ranking logic through a clean user interface:
```bash
streamlit run app.py
```
Upload the `sample_candidates.json` file into the UI to see a real-time data table showing score breakdowns and generated reasoning for each candidate!

---

## 📂 Repository Structure

```text
📦 redrob-orvix-ranker
 ┣ 📂 src/
 ┃ ┣ 📜 jd_profile.py   # System weights, constants, and keywords
 ┃ ┣ 📜 honeypot.py     # Layer 1 detection rules
 ┃ ┣ 📜 scorer.py       # Layer 2 & 3 evaluation engine
 ┃ ┗ 📜 output.py       # Deterministic reasoning generation
 ┣ 📂 tests/
 ┃ ┗ 📜 test_scorer.py  # Validation of edge cases & logic
 ┣ 📜 rank.py           # Main CLI pipeline script
 ┣ 📜 app.py            # Streamlit Sandbox UI
 ┣ 📜 requirements.txt  # Project dependencies
 ┗ 📜 submission_metadata.yaml
```

*Built with ❤️ by Team Orvix.*
