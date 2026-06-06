import csv
import json
import logging
import sys
from pathlib import Path
from typing import Optional
from config import SCORER_WEIGHTS, TOP_K
from scorers import (
    score_title_role,
    score_skills,
    score_career_quality,
    score_experience,
    score_statement,
    score_behavioral,
    score_location,
    score_education,
)
from honeypot import detect_honeypot

logger = logging.getLogger(__name__)

SCORER_FUNCTIONS = {
    "title_role": score_title_role,
    "skills": score_skills,
    "career_quality": score_career_quality,
    "experience": score_experience,
    "statement": score_statement,
    "behavioral": score_behavioral,
    "location": score_location,
    "education": score_education,
}


def generate_reasoning(candidate: dict, sub_scores: dict, final: float, honeypot: dict) -> str:
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})

    current_title = profile.get("current_title", "Unknown")
    yoe = profile.get("years_of_experience", 0)
    company = profile.get("current_company", "")
    location = profile.get("location", "")
    country = profile.get("country", "")
    skills = candidate.get("skills", [])
    education = candidate.get("education", [])
    summary = (profile.get("summary") or "")[:200]

    parts = []

    # --- 1. Title match ---
    ts = sub_scores.get("title_role", 0)
    if ts >= 0.9:
        parts.append(f"Strong title: {current_title}")
    elif ts >= 0.5:
        parts.append(f"Good title: {current_title}")
    elif ts >= 0.2:
        parts.append(f"Adjacent title: {current_title}")
    else:
        parts.append(f"Weak title: {current_title}")

    # --- 2. Top skills (pick 2-3 most relevant) ---
    top_skills = sorted(
        [s for s in skills if s.get("proficiency") in ("expert", "advanced")],
        key=lambda s: s.get("endorsements", 0),
        reverse=True,
    )[:3]
    if not top_skills:
        top_skills = sorted(skills, key=lambda s: s.get("endorsements", 0), reverse=True)[:2]

    if top_skills:
        skill_names = [s.get("name", "") for s in top_skills if s.get("name")]
        if skill_names:
            parts.append(f"Skills: {', '.join(skill_names[:3])}")

    # --- 3. Career highlights ---
    if company:
        parts.append(f"@{company}")

    # --- 4. Education ---
    best_edu = ""
    for edu in education:
        deg = edu.get("degree", "")
        field = edu.get("field_of_study", "")
        if deg or field:
            best_edu = f"{deg} {field}".strip()
    if best_edu:
        # Truncate long strings
        if len(best_edu) > 50:
            best_edu = best_edu[:50] + "..."
        parts.append(f"Edu: {best_edu}")

    # --- 5. Statement fit ---
    ss = sub_scores.get("statement", 0)
    if ss >= 0.5:
        parts.append("Statement shows strong ML intent")
    elif ss >= 0.2:
        parts.append("Statement hints at ML interest")
    elif summary:
        parts.append("No ML signals in statement")

    # --- 6. Honest gap / concern (if any) ---
    gaps = []
    if yoe < 2:
        gaps.append(f"only {yoe}yr exp")
    elif yoe > 15:
        gaps.append(f"{yoe}yr may exceed startup preference")
    if ts < 0.3 and sub_scores.get("skills", 0) < 0.3:
        gaps.append("limited ML alignment in title+skills")
    if honeypot.get("is_honeypot"):
        gaps.append("honeypot flags present")

    # Build the score line
    score_line = f"Score={final:.4f}"
    bonus_parts = []
    for name in SCORER_WEIGHTS:
        s = sub_scores.get(name, 0)
        w = SCORER_WEIGHTS[name]
        bonus_parts.append(f"{name}={s:.3f}")

    if gaps:
        score_line += f" | Gap: {'; '.join(gaps[:2])}"

    parts.append(score_line)
    parts.append("(" + "; ".join(bonus_parts) + ")")

    return " | ".join(parts)


def score_candidate(candidate: dict) -> dict:
    sub_scores = {}
    reasonings = {}

    for name, func in SCORER_FUNCTIONS.items():
        result = func(candidate)
        sub_scores[name] = result["score"]
        reasonings[name] = result["reasoning"]

    honeypot = detect_honeypot(candidate)
    honey_penalty = honeypot["penalty"]

    weighted_sum = sum(
        sub_scores[name] * SCORER_WEIGHTS.get(name, 0)
        for name in sub_scores
    )
    final = weighted_sum * (1 - honey_penalty)

    profile = candidate.get("profile", {})
    current_title = profile.get("current_title", "Unknown")
    yoe = profile.get("years_of_experience", 0)

    reason_short = generate_reasoning(candidate, sub_scores, final, honeypot)

    return {
        "candidate_id": candidate["candidate_id"],
        "score": round(final, 4),
        "sub_scores": sub_scores,
        "reasonings": reasonings,
        "honeypot": honeypot,
        "profile": candidate.get("profile", {}),
        "reasoning_short": reason_short,
    }


def load_candidates(path: str) -> list:
    p = Path(path)
    candidates = []
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                candidates.append(json.loads(line))
    return candidates


def rank_candidates(
    candidates_path: str,
    output_path: str = "submission.csv",
    top_k: int = TOP_K,
    verbose: bool = False,
) -> list[dict]:
    logger.info("Loading candidates from %s ...", candidates_path)
    candidates = load_candidates(candidates_path)
    logger.info("Loaded %d candidates.", len(candidates))

    logger.info("Scoring %d candidates ...", len(candidates))
    results = []
    for i, c in enumerate(candidates):
        if verbose and (i + 1) % 10000 == 0:
            logger.info("  scored %d / %d", i + 1, len(candidates))
        result = score_candidate(c)
        results.append(result)

    results.sort(key=lambda r: (-r["score"], r["candidate_id"]))

    top = results[:top_k]

    logger.info("Writing top %d to %s ...", top_k, output_path)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for rank, entry in enumerate(top, start=1):
            writer.writerow([
                entry["candidate_id"],
                rank,
                f"{entry['score']:.4f}",
                entry["reasoning_short"],
            ])

    logger.info("Done. Submission written to %s", output_path)
    return top
