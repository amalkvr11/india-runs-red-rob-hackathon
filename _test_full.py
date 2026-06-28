import json, sys, time, traceback
from pathlib import Path
sys.path.insert(0, '.')
from ranker import score_candidate, load_candidates

path = r'[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl'
print(f'Loading {path}...')
candidates = load_candidates(path)
print(f'Loaded {len(candidates)} candidates')

start = time.time()
errors = []
for i, c in enumerate(candidates):
    try:
        r = score_candidate(c)
    except Exception as e:
        errors.append((i, c.get('candidate_id', '?'), str(e)))
        if len(errors) >= 5:
            break
    if (i+1) % 10000 == 0:
        elapsed = time.time() - start
        print(f'  Scored {i+1}/{len(candidates)} ({elapsed:.1f}s)')

if errors:
    print(f'ERRORS ({len(errors)}):')
    for idx, cid, err in errors:
        print(f'  #{idx} ({cid}): {err}')
else:
    print(f'ALL {len(candidates)} scored successfully in {time.time()-start:.1f}s')
