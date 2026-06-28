import json, sys, time
from pathlib import Path
sys.path.insert(0, '.')
from ranker import score_candidate, load_candidates

path = r'[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl'
candidates = load_candidates(path)
print(f'Loaded {len(candidates)} candidates')

# Score first 10 to verify
for i in range(min(10, len(candidates))):
    r = score_candidate(candidates[i])
    print(f'  #{i}: id={r["candidate_id"]} score={r["score"]:.4f}  sub_scores={r["sub_scores"]}')
    print(f'       honeypot={r["honeypot"]["is_honeypot"]} flags={r["honeypot"]["flags"]}')
    print(f'       reasoning={r["reasoning_short"][:120]}...')
