# Redrob Candidate Ranker

**India Runs Data & AI Challenge** by Redrob — Rank 100K+ candidates for a Senior AI Engineer role at a Series A startup.

## Quick Start

```bash
# 1. Run the ranking pipeline
python rank.py --candidates ./candidates.jsonl --out ./submission.csv

# 2. Validate
python validate_submission.py --submission ./submission.csv
```

## Architecture

```
candidates.jsonl
      |
      v
  honeypot.py ──> detect_honeypot()    7+ anomaly signals
  scorers.py  ──> 8 scoring modules     title_role, skills, career_quality,
                                        experience, statement, behavioral,
                                        location, education
      |
      v
  ranker.py   ──> score + rank          weighted sum → sort → top 100
      |
      v
  submission.csv                        4 columns, 100 rows
```

## Scoring Methodology

| Dimension | Weight | Measures |
|-----------|--------|----------|
| Title/Role | 0.22 | Current title match against AI/ML tiers (1.0 direct → 0.0 irrelevant) |
| Skills | 0.18 | Relevance across 6 groups + proficiency × endorsements × duration |
| Career Quality | 0.18 | Tenure stability, seniority progression, production exposure, company diversity |
| Experience | 0.13 | Ideal 3–10 YoE, blended with ML keyword density in descriptions |
| Statement | 0.10 | Self-reported ML intent, startup affinity, impact language in summary/statement |
| Behavioral | 0.09 | Recency, open-to-work, response rate, verification, GitHub, salary alignment |
| Location | 0.05 | India tech hub preference (Bangalore, Hyderabad, Pune, Gurgaon, etc.) + relocation |
| Education | 0.05 | Degree level (PhD>MTech>BTech), institution tier, CS-related field |

**Final Score** = (Weighted Sum) × (1 − Honeypot Penalty)

### Title Tier System

- **1.0**: `ai engineer`, `ml engineer`, `machine learning engineer`, `nlp engineer`, `ranking engineer`
- **0.9**: `data scientist`, `applied scientist`, `recommendation engineer`
- **0.7**: `data engineer`, `backend engineer`
- **0.5**: `software engineer`
- **0.0**: Non-technical roles (`hr manager`, `accountant`, `sales executive`, etc.)

### Key Boosters

- Description text containing ML keywords rescues generic titles (+0.4 floor)
- Consulting firm affiliation penalty (−0.3)
- Statement showing ML intent and startup mindset (+statement score)

## Honeypot Detection

The dataset contains synthetic "honeypot" profiles designed to catch naive rankers.
If >10% of your top 100 are honeypots, your submission is **disqualified**.

Our detection flags:

1. **Many expert skills, low endorsements** — impossible to be expert in 6+ skills with <3 avg endorsements
2. **YOE / career history mismatch** — claimed experience exceeds career history by 4+ years
3. **Assessment contradiction** — expert/advanced skill with near-zero assessment score
4. **Future activity date** — `last_active_date` ahead of reference date
5. **Unrealistic YOE** — >50 years experience
6. **Excessive skills** — >30 skills (script-generated profiles)
7. **All assessments very low** — systematic low scores across many assessments
8. **Too many career entries** — >15 entries (generated)
9. **Missing required fields** — no title, YOE, or location

Each flag adds severity up to a max penalty of **0.6×**.

## Running the API + Frontend

### Option A: Start script

```bash
start.bat   # Windows CMD
# or
./start.ps1 # PowerShell
```

### Option B: Manual

```bash
# Terminal 1 — API
uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 — Frontend
cd frontend
npm install
npm run dev
```

Then open **http://localhost:3000**.

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/weights` | Return scorer weights |
| GET | `/api/status` | Check if results are cached |
| POST | `/api/rank` | Run ranking (upload file or use default) |
| GET | `/api/results` | Get cached results |
| GET | `/api/download` | Download submission.csv |

## Project Structure

```
.
├── rank.py                 # CLI entry point (spec-compliant)
├── main.py                 # Alternative CLI entry
├── config.py               # Central configuration (weights, thresholds)
├── scorers.py              # 8 scoring modules
├── honeypot.py             # Fraud detection
├── ranker.py               # Pipeline orchestrator + reasoning
├── api/
│   └── server.py           # FastAPI backend
├── frontend/
│   ├── src/
│   │   ├── App.vue         # Root layout (sidebar, topbar)
│   │   ├── main.js         # Vue bootstrap
│   │   ├── router/         # 6 routes
│   │   ├── stores/         # Pinia store
│   │   └── views/          # Dashboard, Results, Detail, Stats, Export, About
│   ├── package.json
│   └── vite.config.js
├── submission.csv          # Generated output
├── submission_metadata.yaml
├── requirements.txt
├── start.bat
└── start.ps1
```

## Requirements

- Python 3.10+
- 16 GB RAM (for the full 100K pipeline)
- CPU only (no GPU needed)
- ~60–120 seconds for 100K candidates

### Python Dependencies

```
fastapi>=0.110.0
uvicorn>=0.27.0
python-multipart>=0.0.9
```

### Node Dependencies (Frontend)

```
vue ^3.5, vue-router ^4.5, pinia ^3.0,
primevue ^4.3, @primevue/themes ^4.3, primeicons ^7.0,
apexcharts ^4.5, vue3-apexcharts ^1.11,
animate.css ^4.1, @vueuse/core ^12.0
```

## Performance

| Metric | Value |
|--------|-------|
| Candidates | 100,000 |
| Time | ~64s (single-threaded) |
| Memory | ~4 GB peak |
| CPU | 1 core |
| Disk (output) | ~15 KB (submission.csv) |
| Network | None |
