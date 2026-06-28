import json
import pytest
from scorers import (
    score_title_role, score_skills, score_career_quality,
    score_experience, score_education, score_behavioral, score_statement
)
from honeypot import detect_honeypot


def create_test_candidate(
    candidate_id="TEST001",
    title="ML Engineer",
    company="Google",
    yoe=5.0,
    skills=None,
    education=None,
    location="Bangalore",
    has_ml_description=True
):
    candidate = {
        "candidate_id": candidate_id,
        "profile": {
            "current_title": title,
            "current_company": company,
            "years_of_experience": yoe,
            "location": location,
            "country": "India",
            "summary": "Machine learning engineer passionate about building AI systems" if has_ml_description else "Software developer",
            "statement": "Looking to work on cutting-edge ML and deep learning projects at a startup" if has_ml_description else ""
        },
        "career_history": [
            {
                "title": title,
                "company": company,
                "start_date": "2021-01-01",
                "end_date": None,
                "duration_months": 48,
                "is_current": True,
                "description": "Building ML models and deploying them to production" if has_ml_description else "General software development"
            }
        ],
        "skills": skills or [
            {"name": "Python", "proficiency": "expert", "endorsements": 15, "duration_months": 48},
            {"name": "PyTorch", "proficiency": "advanced", "endorsements": 12, "duration_months": 36},
            {"name": "Embeddings", "proficiency": "advanced", "endorsements": 10, "duration_months": 24},
        ],
        "education": education or [
            {
                "institution": "IIT Delhi",
                "degree": "B.Tech",
                "field_of_study": "Computer Science",
                "tier": "tier_1"
            }
        ],
        "redrob_signals": {
            "last_active_date": "2026-05-25",
            "open_to_work_flag": True,
            "verified_email": True,
            "verified_phone": True,
            "linkedin_connected": True,
            "github_activity_score": 75,
            "profile_completeness_score": 85,
            "recruiter_response_rate": 0.8,
            "avg_response_time_hours": 24,
            "notice_period_days": 30,
            "expected_salary_range_inr_lpa": {"min": 25, "max": 40}
        }
    }
    return candidate


def test_title_matching():
    candidate = create_test_candidate(title="ML Engineer")
    result = score_title_role(candidate)
    assert result["score"] >= 0.95, f"Expected score >= 0.95 for 'ML Engineer', got {result['score']}"
    
    candidate = create_test_candidate(title="Senior ML Engineer")
    result = score_title_role(candidate)
    assert result["score"] >= 0.95, f"Expected score >= 0.95 for 'Senior ML Engineer', got {result['score']}"
    
    candidate = create_test_candidate(title="Backend Engineer", has_ml_description=True)
    result = score_title_role(candidate)
    assert result["score"] >= 0.4, f"Expected score >= 0.4 with ML description boost, got {result['score']}"
    
    candidate = create_test_candidate(title="HR Manager")
    result = score_title_role(candidate)
    assert result["score"] < 0.1, f"Expected score < 0.1 for 'HR Manager', got {result['score']}"


def test_skills_scoring():
    skills = [
        {"name": "Python", "proficiency": "expert", "endorsements": 20, "duration_months": 60},
        {"name": "PyTorch", "proficiency": "advanced", "endorsements": 15, "duration_months": 48},
        {"name": "Embeddings", "proficiency": "advanced", "endorsements": 10, "duration_months": 36},
        {"name": "RAG", "proficiency": "intermediate", "endorsements": 8, "duration_months": 24},
        {"name": "Pinecone", "proficiency": "intermediate", "endorsements": 5, "duration_months": 18},
    ]
    candidate = create_test_candidate(title="ML Engineer", skills=skills)
    result = score_skills(candidate)
    assert result["score"] >= 0.5, f"Expected good ML skills score >= 0.5, got {result['score']}"
    
    skills = [
        {"name": "Excel", "proficiency": "expert", "endorsements": 50, "duration_months": 120},
        {"name": "PowerPoint", "proficiency": "advanced", "endorsements": 40, "duration_months": 100},
    ]
    candidate = create_test_candidate(title="ML Engineer", skills=skills, has_ml_description=False)
    result = score_skills(candidate)
    assert result["score"] < 0.3, f"Expected low score for non-ML skills < 0.3, got {result['score']}"


def test_honeypot_detection():
    candidate = create_test_candidate()
    result = detect_honeypot(candidate)
    assert result["is_honeypot"] == False, "Normal candidate should not be flagged as honeypot"
    assert result["penalty"] < 0.15, f"Penalty too high for normal candidate: {result['penalty']}"
    
    skills = [{"name": f"Skill_{i}", "proficiency": "expert", "endorsements": 1, "duration_months": 3} for i in range(10)]
    candidate = create_test_candidate(
        title="ML Engineer",
        skills=skills,
        yoe=100.0
    )
    candidate["profile"]["years_of_experience"] = 100.0
    result = detect_honeypot(candidate)
    assert result["is_honeypot"] == True, "Suspicious candidate should be flagged as honeypot"
    assert result["penalty"] > 0.15, f"Penalty should be significant for honeypot: {result['penalty']}"


def test_career_quality():
    candidate = create_test_candidate()
    result = score_career_quality(candidate)
    assert result["score"] > 0.3, f"Career quality should be reasonable: {result['score']}"
    
    candidate["career_history"].append({
        "title": "Junior ML Engineer",
        "company": "Previous Company",
        "start_date": "2019-01-01",
        "end_date": "2020-12-31",
        "duration_months": 24,
        "is_current": False,
        "description": "Started ML journey with basic models"
    })
    result = score_career_quality(candidate)
    assert result["score"] > 0.35, f"Career progression should improve score: {result['score']}"


def test_experience_scoring():
    candidate = create_test_candidate(yoe=5.0)
    result = score_experience(candidate)
    assert 0.5 <= result["score"] <= 1.0, f"Optimal YOE should score well: {result['score']}"
    
    candidate = create_test_candidate(yoe=1.5)
    result = score_experience(candidate)
    assert result["score"] < 0.8, f"Low YOE should have lower score: {result['score']}"
    
    candidate = create_test_candidate(yoe=20.0)
    result = score_experience(candidate)
    assert result["score"] < 0.95, f"Very high YOE should have lower score: {result['score']}"


def test_education_scoring():
    candidate = create_test_candidate(education=[
        {"institution": "IIT Bombay", "degree": "B.Tech", "field_of_study": "Computer Science", "tier": "tier_1"}
    ])
    result = score_education(candidate)
    assert result["score"] > 0.2, f"Tier 1 CS education should score well: {result['score']}"
    
    candidate = create_test_candidate(education=[
        {"institution": "IIT Delhi", "degree": "Ph.D", "field_of_study": "Machine Learning", "tier": "tier_1"}
    ])
    result = score_education(candidate)
    assert result["score"] > 0.25, f"PhD in ML should score well: {result['score']}"


def test_integration():
    candidate = create_test_candidate()
    
    scores = {}
    for name, func in [
        ("title_role", score_title_role),
        ("skills", score_skills),
        ("career_quality", score_career_quality),
        ("experience", score_experience),
        ("education", score_education),
        ("behavioral", score_behavioral),
        ("statement", score_statement),
    ]:
        result = func(candidate)
        scores[name] = result["score"]
        assert 0.0 <= result["score"] <= 1.0, f"{name} score out of range: {result['score']}"
    
    honeypot_result = detect_honeypot(candidate)
    assert 0.0 <= honeypot_result["penalty"] <= 0.75


if __name__ == "__main__":
    test_title_matching()
    print("[PASS] Title matching tests passed")
    
    test_skills_scoring()
    print("[PASS] Skills scoring tests passed")
    
    test_honeypot_detection()
    print("[PASS] Honeypot detection tests passed")
    
    test_career_quality()
    print("[PASS] Career quality tests passed")
    
    test_experience_scoring()
    print("[PASS] Experience scoring tests passed")
    
    test_education_scoring()
    print("[PASS] Education scoring tests passed")
    
    test_integration()
    print("[PASS] Integration tests passed")
    
    print("\n[SUCCESS] All tests passed successfully!")
