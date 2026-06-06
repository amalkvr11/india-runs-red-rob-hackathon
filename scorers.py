import re
from datetime import datetime, date
from config import (
    REFERENCE_DATE, TITLE_TIERS, ML_DESCRIPTION_KEYWORDS, PRODUCTION_KEYWORDS,
    SKILL_GROUPS, PROFICIENCY_WEIGHTS, CONSULTING_FIRMS,
    INDIA_PREFERRED_CITIES, INDIA_KEYWORDS, CS_RELATED_FIELDS,
    TIER_SCORES, DEGREE_LEVEL_SCORES, BEHAVIORAL_WEIGHTS,
    JD_SALARY_RANGE_LPA,
    STATEMENT_ML_KEYWORDS, STATEMENT_STARTUP_KEYWORDS, STATEMENT_IMPACT_KEYWORDS,
)


def score_title_role(candidate: dict) -> dict:
    profile = candidate["profile"]
    current_title = (profile.get("current_title") or "").lower().strip()

    best = 0.0
    matched_key = ""
    for key, score in TITLE_TIERS.items():
        if key in current_title:
            if score > best:
                best = score
                matched_key = key

    raw_score = best

    title_lower = current_title
    desc_text = " ".join(
        e.get("description", "") or ""
        for e in candidate.get("career_history", [])
    ).lower()

    for kw in ML_DESCRIPTION_KEYWORDS:
        if kw.lower() in desc_text:
            raw_score = max(raw_score, 0.4)
            break

    has_consulting = any(
        firm in (profile.get("current_company") or "").lower()
        for firm in CONSULTING_FIRMS
    )
    penalty = 0.3 if has_consulting else 0.0
    final = max(0.0, raw_score - penalty)

    parts = [f"title={current_title[:40]}"]
    if matched_key:
        parts.append(f"tier={best}")
    if penalty:
        parts.append(f"consulting_penalty={penalty}")
    if raw_score != best:
        parts.append("ml_desc_boost")

    return {"score": final, "reasoning": "; ".join(parts)}


def score_skills(candidate: dict) -> dict:
    skills = candidate.get("skills", [])
    skill_names_lower = {s.get("name", "").lower().strip() for s in skills}

    group_scores = {}
    group_details = []
    total_weighted = 0.0
    total_max = 0.0

    for group_name, max_score, keywords in SKILL_GROUPS:
        matched_keywords = []
        matched_skills = []
        for s in skills:
            sn = s.get("name", "").lower().strip()
            for kw in keywords:
                if kw.lower() in sn and sn not in matched_skills:
                    matched_skills.append(sn)
                    matched_keywords.append(kw)
                    prof = s.get("proficiency", "intermediate").lower()
                    prof_w = PROFICIENCY_WEIGHTS.get(prof, 0.5)
                    endorsements = s.get("endorsements", 0)
                    end_w = min(endorsements / 50, 1.0)
                    dur = s.get("duration_months", 0)
                    dur_w = min(dur / 36, 1.0)
                    combined = 0.5 * prof_w + 0.25 * end_w + 0.25 * dur_w
                    total_weighted += combined * max_score
                    break

        has_group = any(
            any(kw.lower() in sn for kw in keywords)
            for s in skills
            for sn in [s.get("name", "").lower().strip()]
        )
        if has_group:
            group_scores[group_name] = max_score
            total_max += max_score
            group_details.append(group_name)

    if total_max > 0:
        raw = total_weighted / total_max
    else:
        raw = 0.0

    final = min(raw, 1.0)
    return {
        "score": final,
        "reasoning": f"groups={group_details}; score={final:.3f}"
    }


def score_career_quality(candidate: dict) -> dict:
    profile = candidate["profile"]
    history = candidate.get("career_history", [])

    tenure_stability = 0.0
    if history:
        durations = [e.get("duration_months", 0) for e in history]
        avg_dur = sum(durations) / len(durations) if durations else 0
        tenure_stability = min(avg_dur / 36, 1.0)

    growth_progression = 0.0
    for i in range(len(history) - 1):
        curr_title = (history[i].get("title") or "").lower()
        next_title = (history[i + 1].get("title") or "").lower()
        senior_keywords = ["senior", "lead", "head", "principal", "staff", "chief", "manager", "director", "vp", "sde3", "sde4"]
        curr_seniority = sum(1 for k in senior_keywords if k in curr_title)
        next_seniority = sum(1 for k in senior_keywords if k in next_title)
        if next_seniority > curr_seniority:
            growth_progression += 0.15

    production_exposure = 0.0
    all_desc = " ".join(
        e.get("description", "") or "" for e in history
    ).lower()
    prod_matches = sum(1 for kw in PRODUCTION_KEYWORDS if kw.lower() in all_desc)
    production_exposure = min(prod_matches / len(PRODUCTION_KEYWORDS), 1.0)

    current_tenure = 0
    for e in history:
        if e.get("is_current"):
            current_tenure = e.get("duration_months", 0)
            break
    current_too_long_penalty = 0.0
    if current_tenure > 60:
        current_too_long_penalty = 0.1

    company_diversity = 0.0
    companies = set()
    for e in history:
        c = e.get("company", "").strip()
        if c:
            companies.add(c)
    company_diversity = min(len(companies) * 0.05, 0.2)

    raw = (
        0.30 * tenure_stability +
        0.20 * growth_progression +
        0.30 * production_exposure +
        0.20 * company_diversity
    ) - current_too_long_penalty

    final = max(0.0, min(raw, 1.0))
    return {
        "score": final,
        "reasoning": (
            f"tenure_stab={tenure_stability:.2f}; "
            f"growth={growth_progression:.2f}; "
            f"prod={production_exposure:.2f}; "
            f"company_div={company_diversity:.2f}"
        )
    }


def score_experience(candidate: dict) -> dict:
    profile = candidate["profile"]
    yoe = profile.get("years_of_experience", 0)

    ideal_years = (3, 10)
    if yoe < ideal_years[0]:
        exp_score = yoe / ideal_years[0]
    elif yoe <= ideal_years[1]:
        exp_score = 1.0
    else:
        exp_score = max(0.0, 1.0 - (yoe - ideal_years[1]) * 0.04)

    career_history = candidate.get("career_history", [])
    relevant_months = 0
    all_desc = " ".join(
        e.get("description", "") or "" for e in career_history
    ).lower()
    ml_kw_count = sum(1 for kw in ML_DESCRIPTION_KEYWORDS if kw.lower() in all_desc)
    ml_relevance = min(ml_kw_count / 10, 1.0)

    final = 0.6 * exp_score + 0.4 * ml_relevance
    return {
        "score": final,
        "reasoning": f"yoe={yoe}; ml_relevance={ml_relevance:.2f}"
    }


def score_behavioral(candidate: dict) -> dict:
    signals = candidate.get("redrob_signals", {})
    weights = BEHAVIORAL_WEIGHTS
    parts = {}

    # recency
    last_active_str = signals.get("last_active_date", "")
    ref = REFERENCE_DATE
    if isinstance(ref, date) and not isinstance(ref, datetime):
        ref_dt = datetime(ref.year, ref.month, ref.day)
    else:
        ref_dt = ref
    if last_active_str:
        try:
            last_active = datetime.strptime(last_active_str, "%Y-%m-%d")
            days_since = (ref_dt - last_active).days
            parts["recency"] = max(0.0, 1.0 - days_since / 180)
        except ValueError:
            parts["recency"] = 0.0
    else:
        parts["recency"] = 0.0

    # open_to_work
    parts["open_to_work"] = 1.0 if signals.get("open_to_work_flag") else 0.0

    # response_rate
    parts["response_rate"] = signals.get("recruiter_response_rate", 0.0)

    # response_time (lower is better, cap at 168h = 1 week)
    rt = signals.get("avg_response_time_hours", 168)
    parts["response_time"] = max(0.0, 1.0 - rt / 168)

    # notice_period (prefer shorter)
    np_days = signals.get("notice_period_days", 90)
    parts["notice_period"] = max(0.0, 1.0 - np_days / 90)

    # interview_completion
    parts["interview_completion"] = signals.get("interview_completion_rate", 0.0)

    # verification
    v = 0.0
    if signals.get("verified_email"): v += 0.4
    if signals.get("verified_phone"): v += 0.3
    if signals.get("linkedin_connected"): v += 0.3
    parts["verification"] = v

    # github
    gh = signals.get("github_activity_score", -1)
    parts["github"] = max(0.0, gh / 100) if gh >= 0 else 0.0

    # platform_engagement
    views = signals.get("search_appearance_30d", 0)
    saves = signals.get("saved_by_recruiters_30d", 0)
    apps = signals.get("applications_submitted_30d", 0)
    eng = (views / 500) * 0.4 + (saves / 50) * 0.3 + (apps / 20) * 0.3
    parts["platform_engagement"] = min(eng, 1.0)

    # salary_alignment
    salary = signals.get("expected_salary_range_inr_lpa", {})
    sal_min = salary.get("min", 0)
    sal_max = salary.get("max", 0)
    jd_min = JD_SALARY_RANGE_LPA["min"]
    jd_max = JD_SALARY_RANGE_LPA["max"]
    if sal_max > 0 and sal_min <= sal_max:
        overlap_min = max(sal_min, jd_min)
        overlap_max = min(sal_max, jd_max)
        if overlap_max >= overlap_min:
            sal_range = max(sal_max - sal_min, 1)
            overlap = (overlap_max - overlap_min) / sal_range
            parts["salary_alignment"] = overlap
        else:
            parts["salary_alignment"] = 0.0
    else:
        parts["salary_alignment"] = 0.0

    final = sum(parts.get(k, 0.0) * weights.get(k, 0.0) for k in weights)
    return {
        "score": final,
        "reasoning": "; ".join(f"{k}={parts.get(k, 0):.2f}" for k in weights)
    }


def score_location(candidate: dict) -> dict:
    profile = candidate["profile"]
    location = (profile.get("location") or "").lower()
    country = (profile.get("country") or "").lower()

    parts = {}

    if any(city in location for city in INDIA_PREFERRED_CITIES):
        parts["preferred_city"] = 1.0
    elif country in INDIA_KEYWORDS:
        parts["india_general"] = 0.6
    else:
        parts["outside_india"] = 0.3

    signals = candidate.get("redrob_signals", {})
    if signals.get("willing_to_relocate"):
        parts["willing_relocate"] = 0.2

    base = max(parts.values()) if parts else 0.0
    bonus = parts.get("willing_relocate", 0.0)
    final = min(base + bonus, 1.0)
    return {
        "score": final,
        "reasoning": "; ".join(f"{k}={v}" for k, v in parts.items())
    }


def score_statement(candidate: dict) -> dict:
    profile = candidate.get("profile", {})
    summary = (profile.get("summary") or "").strip()
    statement = (profile.get("statement") or "").strip()
    text = f"{summary} {statement}".lower()

    if not text.strip():
        return {"score": 0.0, "reasoning": "no_statement"}

    ml_matches = sum(1 for kw in STATEMENT_ML_KEYWORDS if kw.lower() in text)
    startup_matches = sum(1 for kw in STATEMENT_STARTUP_KEYWORDS if kw.lower() in text)
    impact_matches = sum(1 for kw in STATEMENT_IMPACT_KEYWORDS if kw.lower() in text)

    ml_density = min(ml_matches / 5, 1.0)
    startup_density = min(startup_matches / 2, 1.0)
    impact_density = min(impact_matches / 4, 1.0)

    raw = 0.55 * ml_density + 0.25 * startup_density + 0.20 * impact_density
    final = min(raw, 1.0)

    parts = []
    if ml_matches > 0: parts.append(f"ml_kw={ml_matches}")
    if startup_matches > 0: parts.append(f"startup_kw={startup_matches}")
    if impact_matches > 0: parts.append(f"impact_kw={impact_matches}")

    return {
        "score": final,
        "reasoning": "; ".join(parts) if parts else "no_signals",
    }


def score_education(candidate: dict) -> dict:
    education = candidate.get("education", [])
    if not education:
        return {"score": 0.0, "reasoning": "no_education"}

    best_degree_score = 0.0
    best_tier_score = 0.0
    is_cs_field = False
    details = []

    for edu in education:
        degree = (edu.get("degree") or "").lower().strip()
        field = (edu.get("field_of_study") or "").lower().strip()
        tier = edu.get("tier", "unknown")

        degree_score = 0.0
        for deg_key, dscore in DEGREE_LEVEL_SCORES.items():
            if deg_key.lower() in degree:
                degree_score = max(degree_score, dscore)

        tier_score = TIER_SCORES.get(tier, 0.0)

        field_cs = any(cs_kw in field for cs_kw in CS_RELATED_FIELDS)

        combined = degree_score + tier_score
        if field_cs:
            combined += 0.05

        if combined > best_degree_score + best_tier_score + (0.05 if is_cs_field else 0):
            best_degree_score = degree_score
            best_tier_score = tier_score
            is_cs_field = field_cs

        details.append(
            f"{degree}/{field}/{tier}={degree_score}+{tier_score}"
            f"{'+cs' if field_cs else ''}"
        )

    final = best_degree_score + best_tier_score + (0.05 if is_cs_field else 0)
    final = min(final, 0.35)
    return {
        "score": final,
        "reasoning": "; ".join(details)
    }
