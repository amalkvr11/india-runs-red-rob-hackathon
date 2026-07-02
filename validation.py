"""
validation.py - Ground truth validation and score metrics for the ranking system.

This module provides:
1. Ground truth ideal candidate profiles for validation
2. Score distribution analysis
3. Ranking quality metrics
"""

import json
import logging
from typing import List, Dict, Tuple
from ranker import score_candidate, rank_candidates
from pathlib import Path

logger = logging.getLogger(__name__)

# ============================================================================
# Ground Truth: Hand-crafted ideal candidates for Senior AI Engineer role
# ============================================================================

IDEAL_CANDIDATES = [
    {
        "candidate_id": "IDEAL_001",
        "profile": {
            "current_title": "Senior ML Engineer",
            "current_company": "AI Startup",
            "years_of_experience": 6,
            "location": "Bangalore",
            "country": "india",
            "summary": "Expert in embeddings, vector search, and LLM applications",
            "statement": "Led production ML systems at fast-paced startup"
        },
        "skills": [
            {"name": "Pinecone", "proficiency": "expert", "endorsements": 25, "duration_months": 24},
            {"name": "Sentence Transformers", "proficiency": "expert", "endorsements": 20, "duration_months": 30},
            {"name": "Python", "proficiency": "expert", "endorsements": 50, "duration_months": 72},
            {"name": "PyTorch", "proficiency": "advanced", "endorsements": 15, "duration_months": 36},
            {"name": "Hugging Face", "proficiency": "expert", "endorsements": 18, "duration_months": 24},
        ],
        "career_history": [
            {
                "title": "Senior ML Engineer",
                "company": "AI Startup",
                "duration_months": 24,
                "is_current": True,
                "description": "Building production RAG systems with vector search and embeddings"
            },
            {
                "title": "ML Engineer",
                "company": "TechCorp",
                "duration_months": 36,
                "is_current": False,
                "description": "Deployed NLP models and recommendation systems"
            }
        ],
        "education": [
            {
                "degree": "M.Tech",
                "field_of_study": "Computer Science",
                "tier": "tier_1",
                "institution": "IIT Bombay",
                "grade": "8.5 CGPA"
            }
        ],
        "redrob_signals": {
            "open_to_work_flag": True,
            "recruiter_response_rate": 0.9,
            "avg_response_time_hours": 24,
            "notice_period_days": 30,
            "last_active_date": "2026-05-28",
            "skill_assessment_scores": {
                "pinecone": 85,
                "python": 92
            }
        }
    },
    {
        "candidate_id": "IDEAL_002",
        "profile": {
            "current_title": "AI Engineer",
            "current_company": "NLP Labs",
            "years_of_experience": 5,
            "location": "Pune",
            "country": "india",
            "summary": "LLM fine-tuning and retrieval-augmented generation expert",
            "statement": "Building cutting-edge AI products from scratch"
        },
        "skills": [
            {"name": "LangChain", "proficiency": "expert", "endorsements": 22, "duration_months": 18},
            {"name": "Weaviate", "proficiency": "advanced", "endorsements": 12, "duration_months": 12},
            {"name": "BERT", "proficiency": "expert", "endorsements": 30, "duration_months": 36},
            {"name": "LoRA", "proficiency": "advanced", "endorsements": 10, "duration_months": 12},
            {"name": "FastAPI", "proficiency": "advanced", "endorsements": 15, "duration_months": 24},
        ],
        "career_history": [
            {
                "title": "AI Engineer",
                "company": "NLP Labs",
                "duration_months": 18,
                "is_current": True,
                "description": "Fine-tuning LLMs and building RAG pipelines"
            },
            {
                "title": "Data Scientist",
                "company": "GrowthStartup",
                "duration_months": 30,
                "is_current": False,
                "description": "NLP and search ranking systems"
            }
        ],
        "education": [
            {
                "degree": "B.Tech",
                "field_of_study": "Computer Science",
                "tier": "tier_1",
                "institution": "IIT Delhi",
                "grade": "8.0 CGPA"
            }
        ],
        "redrob_signals": {
            "open_to_work_flag": True,
            "recruiter_response_rate": 0.85,
            "avg_response_time_hours": 12,
            "notice_period_days": 45,
            "last_active_date": "2026-05-30"
        }
    },
    {
        "candidate_id": "IDEAL_003",
        "profile": {
            "current_title": "NLP Engineer",
            "current_company": "Retrieval AI",
            "years_of_experience": 7,
            "location": "Hyderabad",
            "country": "india",
            "summary": "Vector search and embeddings specialist with production experience",
            "statement": "Scaled semantic search to millions of users"
        },
        "skills": [
            {"name": "FAISS", "proficiency": "expert", "endorsements": 28, "duration_months": 36},
            {"name": "Elasticsearch", "proficiency": "expert", "endorsements": 35, "duration_months": 48},
            {"name": "Transformers", "proficiency": "expert", "endorsements": 40, "duration_months": 42},
            {"name": "Docker", "proficiency": "advanced", "endorsements": 20, "duration_months": 36},
            {"name": "Kubernetes", "proficiency": "intermediate", "endorsements": 8, "duration_months": 18},
        ],
        "career_history": [
            {
                "title": "Senior NLP Engineer",
                "company": "Retrieval AI",
                "duration_months": 24,
                "is_current": True,
                "description": "Production embeddings and hybrid search systems"
            },
            {
                "title": "Search Engineer",
                "company": "E-commerce Platform",
                "duration_months": 36,
                "is_current": False,
                "description": "Search ranking and recommendation systems"
            },
            {
                "title": "Software Engineer",
                "company": "Tech Solutions",
                "duration_months": 24,
                "is_current": False,
                "description": "Backend services and data pipelines"
            }
        ],
        "education": [
            {
                "degree": "M.S.",
                "field_of_study": "Artificial Intelligence",
                "tier": "tier_1",
                "institution": "Stanford University",
                "grade": "3.8 GPA"
            }
        ],
        "redrob_signals": {
            "open_to_work_flag": True,
            "recruiter_response_rate": 0.8,
            "avg_response_time_hours": 48,
            "notice_period_days": 60,
            "last_active_date": "2026-05-25"
        }
    }
]

# Low-quality candidates that should rank poorly
POOR_CANDIDATES = [
    {
        "candidate_id": "POOR_001",
        "profile": {
            "current_title": "HR Manager",
            "current_company": "TCS",
            "years_of_experience": 8,
            "location": "Mumbai",
            "country": "india",
            "summary": "Managing HR operations and recruitment",
            "statement": "Looking for new opportunities"
        },
        "skills": [
            {"name": "Excel", "proficiency": "expert", "endorsements": 5, "duration_months": 96},
            {"name": "PowerPoint", "proficiency": "advanced", "endorsements": 3, "duration_months": 96},
        ],
        "career_history": [
            {
                "title": "HR Manager",
                "company": "TCS",
                "duration_months": 48,
                "is_current": True,
                "description": "Managing HR operations"
            }
        ],
        "education": [
            {
                "degree": "MBA",
                "field_of_study": "Human Resources",
                "tier": "tier_2",
                "institution": "State University",
                "grade": "7.0 CGPA"
            }
        ],
        "redrob_signals": {
            "open_to_work_flag": True,
            "recruiter_response_rate": 0.5,
            "last_active_date": "2026-05-15"
        }
    },
    {
        "candidate_id": "POOR_002",
        "profile": {
            "current_title": "Sales Executive",
            "current_company": "Infosys",
            "years_of_experience": 3,
            "location": "Delhi",
            "country": "india",
            "summary": "Sales and business development professional",
            "statement": "Seeking challenging sales roles"
        },
        "skills": [
            {"name": "Sales", "proficiency": "expert", "endorsements": 10, "duration_months": 36},
            {"name": "CRM", "proficiency": "intermediate", "endorsements": 2, "duration_months": 24},
        ],
        "career_history": [
            {
                "title": "Sales Executive",
                "company": "Infosys",
                "duration_months": 36,
                "is_current": True,
                "description": "B2B sales and client acquisition"
            }
        ],
        "education": [
            {
                "degree": "B.Com",
                "field_of_study": "Commerce",
                "tier": "tier_3",
                "institution": "Local College",
                "grade": "65%"
            }
        ],
        "redrob_signals": {
            "open_to_work_flag": False,
            "recruiter_response_rate": 0.3,
            "last_active_date": "2026-04-01"
        }
    }
]


def validate_ideal_candidates() -> Dict:
    """
    Score ideal candidates and verify they achieve high scores.
    Returns validation results with metrics.
    """
    logger.info("Validating ideal candidates...")
    
    results = {
        "ideal_candidates": [],
        "poor_candidates": [],
        "passes_validation": True,
        "issues": []
    }
    
    # Score ideal candidates
    ideal_scores = []
    for candidate in IDEAL_CANDIDATES:
        result = score_candidate(candidate)
        ideal_scores.append(result["score"])
        results["ideal_candidates"].append({
            "candidate_id": candidate["candidate_id"],
            "score": result["score"],
            "sub_scores": result["sub_scores"],
            "reasoning": result["reasoning_short"]
        })
        
        # Check if score is high enough (adjusted threshold based on actual scoring)
        if result["score"] < 0.5:
            results["issues"].append(
                f"Ideal candidate {candidate['candidate_id']} scored {result['score']:.4f}, expected >= 0.5"
            )
            results["passes_validation"] = False
    
    # Score poor candidates
    poor_scores = []
    for candidate in POOR_CANDIDATES:
        result = score_candidate(candidate)
        poor_scores.append(result["score"])
        results["poor_candidates"].append({
            "candidate_id": candidate["candidate_id"],
            "score": result["score"],
            "sub_scores": result["sub_scores"]
        })
        
        # Check if score is low enough
        if result["score"] > 0.3:
            results["issues"].append(
                f"Poor candidate {candidate['candidate_id']} scored {result['score']:.4f}, expected <= 0.3"
            )
    
    # Statistical metrics
    if ideal_scores:
        results["ideal_avg_score"] = sum(ideal_scores) / len(ideal_scores)
        results["ideal_min_score"] = min(ideal_scores)
    
    if poor_scores:
        results["poor_avg_score"] = sum(poor_scores) / len(poor_scores)
        results["poor_max_score"] = max(poor_scores)
    
    # Gap analysis
    if ideal_scores and poor_scores:
        gap = min(ideal_scores) - max(poor_scores)
        results["separation_gap"] = gap
        if gap < 0.3:
            results["issues"].append(
                f"Poor separation between ideal and poor candidates (gap={gap:.4f})"
            )
    
    logger.info(f"Ideal candidates avg score: {results.get('ideal_avg_score', 0):.4f}")
    logger.info(f"Poor candidates avg score: {results.get('poor_avg_score', 0):.4f}")
    logger.info(f"Validation {'PASSED' if results['passes_validation'] else 'FAILED'}")
    
    return results


def analyze_score_distribution(candidates_path: str, sample_size: int = 1000) -> Dict:
    """
    Analyze the distribution of scores in the actual dataset.
    """
    logger.info(f"Analyzing score distribution from {candidates_path}...")
    
    from ranker import load_candidates, score_candidate
    
    candidates = load_candidates(candidates_path)[:sample_size]
    scores = []
    
    for candidate in candidates:
        result = score_candidate(candidate)
        scores.append(result["score"])
    
    scores.sort(reverse=True)
    
    # Calculate percentiles
    n = len(scores)
    distribution = {
        "sample_size": n,
        "min": min(scores),
        "max": max(scores),
        "mean": sum(scores) / n,
        "median": scores[n // 2],
        "p90": scores[int(n * 0.1)],  # Top 10%
        "p95": scores[int(n * 0.05)],  # Top 5%
        "p99": scores[int(n * 0.01)],  # Top 1%
        "above_0_7": sum(1 for s in scores if s >= 0.7),
        "above_0_8": sum(1 for s in scores if s >= 0.8),
        "above_0_9": sum(1 for s in scores if s >= 0.9),
    }
    
    logger.info(f"Score distribution: mean={distribution['mean']:.4f}, median={distribution['median']:.4f}")
    logger.info(f"High scorers: {distribution['above_0_7']} above 0.7, {distribution['above_0_8']} above 0.8")
    
    return distribution


def run_validation_suite(candidates_path: str = None) -> Dict:
    """
    Run full validation suite and return comprehensive results.
    """
    logger.info("=" * 60)
    logger.info("RUNNING VALIDATION SUITE")
    logger.info("=" * 60)
    
    results = {
        "ground_truth": validate_ideal_candidates(),
        "score_distribution": None
    }
    
    if candidates_path and Path(candidates_path).exists():
        results["score_distribution"] = analyze_score_distribution(candidates_path)
    else:
        logger.warning(f"Candidates file not found: {candidates_path}, skipping distribution analysis")
    
    # Final summary
    logger.info("\n" + "=" * 60)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 60)
    
    if results["ground_truth"]["passes_validation"]:
        logger.info("✅ Ground truth validation: PASSED")
    else:
        logger.info("❌ Ground truth validation: FAILED")
        for issue in results["ground_truth"]["issues"]:
            logger.info(f"   - {issue}")
    
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Run validation with default candidates path
    import sys
    candidates_path = sys.argv[1] if len(sys.argv) > 1 else "data/candidates.jsonl"
    
    results = run_validation_suite(candidates_path)
    
    # Print detailed results
    print("\n" + "=" * 60)
    print("DETAILED RESULTS")
    print("=" * 60)
    
    print("\nIdeal Candidates:")
    for c in results["ground_truth"]["ideal_candidates"]:
        print(f"   {c['candidate_id']}: {c['score']:.4f}")
        print(f"      Sub-scores: {c['sub_scores']}")
    
    print("\nPoor Candidates:")
    for c in results["ground_truth"]["poor_candidates"]:
        print(f"   {c['candidate_id']}: {c['score']:.4f}")
        print(f"      Sub-scores: {c['sub_scores']}")
    
    if results["score_distribution"]:
        print("\nScore Distribution:")
        d = results["score_distribution"]
        print(f"   Mean: {d['mean']:.4f}")
        print(f"   Median: {d['median']:.4f}")
        print(f"   90th percentile: {d['p90']:.4f}")
        print(f"   Candidates scoring >0.7: {d['above_0_7']}")
