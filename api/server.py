import csv
import io
import json
import logging
import os
import time
import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import SCORER_WEIGHTS, TOP_K
from ranker import score_candidate, load_candidates

logger = logging.getLogger(__name__)

app = FastAPI(title="Redrob Ranker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULT_JSONL = (
    Path(__file__).resolve().parent.parent
    / r"[PUB] India_runs_data_and_ai_challenge"
    / r"India_runs_data_and_ai_challenge"
    / "candidates.jsonl"
)

ranking_cache = {"results": None, "timestamp": 0, "cached": False}

class ResultsResponse(BaseModel):
    results: list[dict]
    stats: dict
    elapsed: float

class StatusResponse(BaseModel):
    cached: bool
    timestamp: float
    count: int


@app.get("/api/weights")
def get_weights():
    return SCORER_WEIGHTS


@app.get("/api/status")
def get_status():
    return StatusResponse(
        cached=ranking_cache["cached"],
        timestamp=ranking_cache["timestamp"],
        count=len(ranking_cache["results"]) if ranking_cache["results"] else 0,
    )


@app.post("/api/rank", response_model=ResultsResponse)
async def run_rank(
    file: Optional[UploadFile] = File(None),
    use_default: bool = Form(True),
    top_k: int = Form(100),
):
    start = time.time()

    if file and file.filename:
        content = await file.read()
        text = content.decode("utf-8")
        candidates = [
            json.loads(line) for line in text.strip().split("\n") if line.strip()
        ]
        logger.info("Loaded %d candidates from uploaded file.", len(candidates))
    elif use_default:
        if not DEFAULT_JSONL.exists():
            raise HTTPException(404, f"Default file not found: {DEFAULT_JSONL}")
        candidates = load_candidates(str(DEFAULT_JSONL))
        logger.info("Loaded %d candidates from default file.", len(candidates))
    else:
        raise HTTPException(400, "No file uploaded and use_default is false.")

    results = []
    for i, c in enumerate(candidates):
        r = score_candidate(c)
        results.append(r)

    results.sort(key=lambda r: (-r["score"], r["candidate_id"]))

    top = results[:top_k]
    for rank, entry in enumerate(top, start=1):
        entry["rank"] = rank
        profile = entry.get("profile") or {}
        entry["current_title"] = profile.get("current_title", "Unknown")
        entry["current_company"] = profile.get("current_company", "")
        entry["location"] = (
            f"{profile.get('location', '')}, {profile.get('country', '')}"
        )
        entry["yoe"] = profile.get("years_of_experience", 0)
        entry["name"] = profile.get("anonymized_name", "")

    elapsed = time.time() - start

    scores_list = [r["score"] for r in top]
    stats = {
        "count": len(top),
        "top_score": round(max(scores_list), 4) if scores_list else 0,
        "bottom_score": round(min(scores_list), 4) if scores_list else 0,
        "mean_score": round(sum(scores_list) / len(scores_list), 4) if scores_list else 0,
    }

    ranking_cache["results"] = top
    ranking_cache["timestamp"] = time.time()
    ranking_cache["cached"] = True

    logger.info("Ranked %d candidates in %.1fs", len(candidates), elapsed)

    return ResultsResponse(results=top, stats=stats, elapsed=elapsed)


@app.get("/api/results")
def get_results():
    if not ranking_cache["cached"]:
        raise HTTPException(404, "No results cached. POST /api/rank first.")
    scores_list = [r["score"] for r in ranking_cache["results"]]
    stats = {
        "count": len(ranking_cache["results"]),
        "top_score": round(max(scores_list), 4) if scores_list else 0,
        "bottom_score": round(min(scores_list), 4) if scores_list else 0,
        "mean_score": round(sum(scores_list) / len(scores_list), 4) if scores_list else 0,
    }
    return ResultsResponse(
        results=ranking_cache["results"],
        stats=stats,
        elapsed=0,
    )


@app.get("/api/download")
def download_csv():
    if not ranking_cache["cached"] or not ranking_cache["results"]:
        raise HTTPException(404, "No results. POST /api/rank first.")

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["candidate_id", "rank", "score", "reasoning"])
    for r in ranking_cache["results"]:
        writer.writerow([
            r["candidate_id"],
            r["rank"],
            f"{r['score']:.4f}",
            r.get("reasoning_short", ""),
        ])
    csv_content = buf.getvalue()

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=submission.csv"},
    )


@app.get("/api/candidate/{candidate_id}")
def get_candidate_detail(candidate_id: str):
    """Get detailed information about a specific candidate."""
    if not ranking_cache["cached"] or not ranking_cache["results"]:
        raise HTTPException(404, "No results. POST /api/rank first.")
    
    for r in ranking_cache["results"]:
        if r["candidate_id"] == candidate_id:
            return r
    
    raise HTTPException(404, f"Candidate {candidate_id} not found")


@app.get("/api/explain/{candidate_id}")
def explain_candidate(candidate_id: str):
    """Get SHAP-like explanation for a candidate's ranking."""
    from explainability import ShapExplainer
    
    if not ranking_cache["cached"] or not ranking_cache["results"]:
        raise HTTPException(404, "No results. POST /api/rank first.")
    
    for r in ranking_cache["results"]:
        if r["candidate_id"] == candidate_id:
            explainer = ShapExplainer()
            explanation = explainer.explain_candidate(
                r,
                r.get("sub_scores", {}),
                r.get("score", 0),
                r.get("honeypot", {}).get("penalty", 0)
            )
            return explanation
    
    raise HTTPException(404, f"Candidate {candidate_id} not found")


@app.get("/api/ml-similarity/{candidate_id}")
def get_ml_similarity(candidate_id: str):
    """Get ML-based semantic similarity score for a candidate."""
    from ml_similarity import score_ml_similarity
    
    if not ranking_cache["cached"] or not ranking_cache["results"]:
        raise HTTPException(404, "No results. POST /api/rank first.")
    
    for r in ranking_cache["results"]:
        if r["candidate_id"] == candidate_id:
            # Need to reload full candidate data
            from ranker import load_candidates
            full_candidates = load_candidates(str(DEFAULT_JSONL))
            for fc in full_candidates:
                if fc["candidate_id"] == candidate_id:
                    return score_ml_similarity(fc)
    
    raise HTTPException(404, f"Candidate {candidate_id} not found")


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "cached": ranking_cache["cached"]}


if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    uvicorn.run(app, host="0.0.0.0", port=8000)
