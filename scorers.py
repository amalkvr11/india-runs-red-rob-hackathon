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


def title_match_score(title: str) -> tuple:
    title_lower = title.lower().strip()
    tokens = re.split(r'[\s\-_/,.]+', title_lower)
    tokens = [t for t in tokens if t]
    
    best_score = 0.0
    best_match = ""
    
    for key, score in TITLE_TIERS.items():
        key_lower = key.lower()
        key_tokens = set(re.split(r'[\s\-_/,.]+', key_lower))
        
        if key_lower == title_lower:
            return score, key, "exact"
        
        if key_lower in title_lower:
            if score > best_score:
                best_score = score
                best_match = key
        
        overlap = len(key_tokens & set(tokens))
        if overlap > 0 and overlap == len(key_tokens):
            if score > best_score:
                best_score = score * 0.98
                best_match = key
    
    seniority_boost = 0.0
    if any(s in title_lower for s in ["senior", "lead", "principal", "staff", "sr"]):
        seniority_boost = 0.05
    elif any(s in title_lower for s in ["junior", "jr", "associate"]):
        seniority_boost = -0.05
    
    if best_score > 0:
        return best_score + seniority_boost, best_match, "partial"
    
    ai_adjacent_keywords = ["ml", "ai", "data", "analytics", "algorithm", "intelligence"]
    ml_adjacent_count = sum(1 for kw in ai_adjacent_keywords if kw in title_lower)
    if ml_adjacent_count >= 2:
        return 0.25, "ai_adjacent_heuristic", "heuristic"
    
    if any(kw in title_lower for kw in ["engineer", "developer", "scientist"]):
        return 0.15, "generic_tech", "heuristic"
    
    return 0.0, "", "no_match"

def score_title_role(candidate: dict) -> dict:
    profile = candidate["profile"]
    current_title = (profile.get("current_title") or "").lower().strip()

    raw_score, matched_key, match_type = title_match_score(current_title)

    history = candidate.get("career_history", [])
    history_titles = [e.get("title", "") or "" for e in history[:5]]
    history_score = 0.0
    history_match = ""
    for h_title in history_titles:
        h_score, h_key, _ = title_match_score(h_title)
        if h_score > history_score:
            history_score = h_score
            history_match = h_key
    
    if history_score > raw_score and history_score >= 0.7:
        raw_score = max(raw_score, history_score * 0.7)
        matched_key = f"{matched_key}+history:{history_match}"

    desc_text = " ".join(
        e.get("description", "") or ""
        for e in history
    ).lower()
    
    ml_matches = sum(1 for kw in ML_DESCRIPTION_KEYWORDS if kw.lower() in desc_text)
    ml_density = min(ml_matches / 8, 1.0)
    
    if ml_density > 0.5 and raw_score < 0.4:
        raw_score = max(raw_score, 0.4)
        ml_boost = True
    else:
        ml_boost = False

    has_consulting = any(
        firm in (profile.get("current_company") or "").lower()
        for firm in CONSULTING_FIRMS
    )
    consulting_penalty = 0.3 if has_consulting else 0.0
    
    if current_company := (profile.get("current_company") or "").lower():
        startup_indicators = ["startup", "labs", "ai", "ml", "tech", "software", "data"]
        if any(ind in current_company for ind in startup_indicators):
            if has_consulting:
                consulting_penalty = min(consulting_penalty, 0.15)
    
    final = max(0.0, raw_score - consulting_penalty)
    
    parts = [f"title={current_title[:40]}"]
    if matched_key:
        parts.append(f"tier={raw_score:.2f}")
    if consulting_penalty:
        parts.append(f"consulting_penalty={consulting_penalty}")
    if ml_boost:
        parts.append("ml_desc_boost")
    if history_match and history_score > 0.7:
        parts.append(f"history_boost:{history_match}")

    return {"score": final, "reasoning": "; ".join(parts)}


def score_skills(candidate: dict) -> dict:
    skills = candidate.get("skills", [])
    profile = candidate.get("profile", {})
    career_history = candidate.get("career_history", [])
    
    for s in skills:
        if s.get("proficiency", "").lower() not in PROFICIENCY_WEIGHTS:
            s["proficiency"] = "intermediate"

    ml_desc_text = " ".join(
        e.get("description", "") or "" for e in career_history
    ).lower()
    has_ml_career = any(kw in ml_desc_text for kw in ["ml", "machine learning", "ai", "deep learning", "nlp"])
    
    group_scores = {}
    group_weighted = {}
    matched_skills_detail = []
    
    core_groups = ["embeddings_retrieval", "vector_db", "nlp_llm"]
    adj_groups = ["ml_frameworks", "ml_eval", "python"]
    infra_groups = ["data_infra"]

    for skill in skills:
        name = skill.get("name", "").lower().strip()
        if not name:
            continue
        
        prof = skill.get("proficiency", "intermediate").lower()
        prof_w = PROFICIENCY_WEIGHTS.get(prof, 0.5)
        
        endorsements = skill.get("endorsements", 0)
        if prof in ("expert", "advanced") and endorsements < 5:
            prof_w *= 0.6
        
        end_w = min(endorsements / 30, 1.0)
        
        dur = skill.get("duration_months", 0)
        dur_w = min(dur / 24, 1.0)
        
        skill_quality = 0.4 * prof_w + 0.35 * end_w + 0.25 * dur_w
    
    total_core_score = 0.0
    core_count = 0
    total_adj_score = 0.0
    adj_count = 0
    
    for group_name, max_score, keywords in SKILL_GROUPS:
        group_matched = []
        group_score = 0.0
        
        for skill in skills:
            sn = (skill.get("name") or "").lower().strip()
            for kw in keywords:
                if kw.lower() in sn:
                    prof = skill.get("proficiency", "intermediate").lower()
                    prof_w = PROFICIENCY_WEIGHTS.get(prof, 0.5)
                    endorsements = skill.get("endorsements", 0)
                    end_w = min(endorsements / 30, 1.0)
                    dur = skill.get("duration_months", 0)
                    dur_w = min(dur / 24, 1.0)
                    quality = 0.4 * prof_w + 0.35 * end_w + 0.25 * dur_w
                    group_score += quality
                    group_matched.append(sn)
                    break
        
        if group_matched:
            capped_score = min(group_score / len(group_matched), 1.0)
            if group_name in core_groups:
                total_core_score += capped_score
                core_count += 1
            elif group_name in adj_groups:
                total_adj_score += capped_score
                adj_count += 1
    
    core_avg = (total_core_score / core_count) if core_count > 0 else 0.0
    adj_avg = (total_adj_score / adj_count) if adj_count > 0 else 0.0
    
    has_core = core_count >= 1
    has_adj = adj_count >= 2
    
    if core_avg >= 0.5:
        final_score = 0.7 * core_avg + 0.3 * adj_avg
    elif has_core:
        final_score = 0.6 * core_avg + 0.4 * adj_avg
    elif has_adj and adj_avg >= 0.6:
        final_score = 0.5 * adj_avg
    else:
        final_score = 0.0
    
    if has_ml_career and not has_core:
        yoe = profile.get("years_of_experience", 0)
        if yoe >= 3:
            final_score *= 0.85
    
    unmatched_ml_skills = []
    for skill in skills:
        name = (skill.get("name") or "").lower()
        if any(ml in name for ml in ["ml", "ai", "machine", "deep", "nlp", "neural", "llm", "gpt", "bert"]):
            found = False
            for group_name, max_score, keywords in SKILL_GROUPS:
                if any(kw.lower() in name for kw in keywords):
                    found = True
                    break
            if not found:
                prof_w = PROFICIENCY_WEIGHTS.get(skill.get("proficiency", "intermediate").lower(), 0.5)
                final_score += 0.05 * prof_w
    
    final = min(final_score, 1.0)
    
    matched_groups = []
    if core_count > 0:
        matched_groups.extend([g for g in core_groups if any(
            any(kw.lower() in (s.get("name") or "").lower() for kw in 
               [kw for gn, ms, kw in SKILL_GROUPS if gn == g][0])
            for s in skills
        )])
    if adj_count > 0:
        matched_groups.extend([g for g in adj_groups if any(
            any(kw.lower() in (s.get("name") or "").lower() for kw in 
               [kw for gn, ms, kw in SKILL_GROUPS if gn == g][0])
            for s in skills
        )])
    
    return {
        "score": final,
        "reasoning": f"core={core_avg:.2f}({core_count}groups); adj={adj_avg:.2f}({adj_count}groups); matched={matched_groups[:4]}"
    }


def score_career_quality(candidate: dict) -> dict:
    profile = candidate.get("profile")
    history = candidate.get("career_history", [])

    tenure_stability = 0.0
    if history:
        durations = [e.get("duration_months", 0) for e in history]
        avg_dur = sum(durations) / len(durations) if durations else 0
        tenure_stability = min(avg_dur / 24, 1.0)
        
        if len(durations) >= 2:
            durations_sorted = sorted(durations, reverse=True)
            top2_avg = sum(durations_sorted[:2]) / 2
            tenure_stability = 0.6 * tenure_stability + 0.4 * min(top2_avg / 36, 1.0)

    growth_progression = 0.0
    seniority_keywords = {
        "entry": ["intern", "trainee", "junior", "jr", "associate", "graduate"],
        "mid": ["engineer", "developer", "analyst", "scientist"],
        "senior": ["senior", "sr", "lead", "principal", "staff", "manager"],
        "executive": ["director", "head", "chief", "vp", "architect"]
    }
    
    title_scores = []
    for entry in history:
        title = (entry.get("title") or "").lower()
        score = 0
        for level, keywords in seniority_keywords.items():
            if any(kw in title for kw in keywords):
                if level == "entry":
                    score = 1
                elif level == "mid":
                    score = 2
                elif level == "senior":
                    score = 3
                elif level == "executive":
                    score = 4
                break
        title_scores.append((entry.get("start_date", ""), score))
    
    title_scores.sort(key=lambda x: x[0])
    
    for i in range(1, len(title_scores)):
        prev_score = title_scores[i-1][1]
        curr_score = title_scores[i][1]
        if curr_score > prev_score:
            growth_progression += 0.12
        elif curr_score == prev_score:
            pass
        else:
            growth_progression -= 0.05
    
    growth_progression = max(0, min(growth_progression, 1.0))

    production_exposure = 0.0
    all_desc = " ".join(
        e.get("description", "") or "" for e in history
    ).lower()
    prod_matches = sum(1 for kw in PRODUCTION_KEYWORDS if kw.lower() in all_desc)
    production_exposure = min(prod_matches / 5, 1.0)

    current_tenure = 0
    company_tenures = {}
    for e in history:
        company = e.get("company", "")
        if e.get("is_current"):
            current_tenure = e.get("duration_months", 0)
        if company:
            company_tenures[company] = company_tenures.get(company, 0) + e.get("duration_months", 0)
    
    current_too_long_penalty = 0.0
    if current_tenure > 72:
        current_too_long_penalty = 0.05
    elif current_tenure > 96:
        current_too_long_penalty = 0.1

    company_diversity = 0.0
    companies = set()
    for e in history:
        c = e.get("company", "").strip()
        if c:
            companies.add(c)
    
    num_companies = len(companies)
    if num_companies <= 1:
        company_diversity = 0.05
    elif num_companies <= 3:
        company_diversity = 0.10 + 0.05 * (num_companies - 1)
    elif num_companies <= 5:
        company_diversity = 0.20 + 0.02 * (num_companies - 3)
    else:
        company_diversity = 0.25

    ml_career_score = 0.0
    ml_keywords = ["ml", "machine learning", "ai", "deep learning", "nlp", "neural", "model", "algorithm"]
    for i, e in enumerate(history[:4]):
        desc = (e.get("description") or "").lower()
        title = (e.get("title") or "").lower()
        ml_match = sum(1 for kw in ml_keywords if kw in desc or kw in title)
        if i == 0:
            ml_career_score += min(ml_match, 3) * 0.15
        else:
            ml_career_score += min(ml_match, 2) * 0.08
    ml_career_score = min(ml_career_score, 1.0)

    raw = (
        0.20 * tenure_stability +
        0.15 * growth_progression +
        0.25 * production_exposure +
        0.10 * company_diversity +
        0.30 * ml_career_score
    ) - current_too_long_penalty

    final = max(0.0, min(raw, 1.0))
    return {
        "score": final,
        "reasoning": (
            f"tenure_stab={tenure_stability:.2f}; "
            f"growth={growth_progression:.2f}; "
            f"prod={production_exposure:.2f}; "
            f"ml_career={ml_career_score:.2f}; "
            f"company_div={company_diversity:.2f}"
        )
    }


def score_experience(candidate: dict) -> dict:
    profile = candidate.get("profile", {})
    yoe = profile.get("years_of_experience", 0)
    history = candidate.get("career_history", [])

    ideal_years = (4, 8)
    if yoe < ideal_years[0]:
        exp_score = (yoe / ideal_years[0]) ** 0.8
    elif yoe <= ideal_years[1]:
        exp_score = 1.0
    else:
        excess_yoe = yoe - ideal_years[1]
        if excess_yoe <= 3:
            exp_score = 0.95
        elif excess_yoe <= 6:
            exp_score = 0.85
        else:
            exp_score = max(0.5, 1.0 - excess_yoe * 0.03)

    ml_relevant_yoe = 0
    ai_ml_keywords = ["ml engineer", "ai engineer", "machine learning", "deep learning", 
                     "data scientist", "nlp", "computer vision", "research scientist",
                     "applied scientist", "recommendation", "ranking", "search"]
    
    for entry in history:
        title = (entry.get("title") or "").lower()
        desc = (entry.get("description") or "").lower()
        duration = entry.get("duration_months", 0) / 12.0
        
        is_ml_role = any(kw in title for kw in ai_ml_keywords)
        has_ml_work = sum(1 for kw in ai_ml_keywords[2:] if kw in desc) >= 3
        
        if is_ml_role:
            ml_relevant_yoe += duration
        elif has_ml_work:
            ml_relevant_yoe += duration * 0.6
    
    ml_relevance_ratio = min(ml_relevant_yoe / max(yoe, 0.1), 1.0) if yoe > 0 else 0.0
    
    all_desc = " ".join(
        e.get("description", "") or "" for e in history
    ).lower()
    ml_kw_count = sum(1 for kw in ML_DESCRIPTION_KEYWORDS if kw.lower() in all_desc)
    ml_density = min(ml_kw_count / 12, 1.0)
    
    ml_relevance = 0.4 * ml_relevance_ratio + 0.6 * ml_density

    current_company = (profile.get("current_company") or "").lower()
    current_title = (profile.get("current_title") or "").lower()
    
    is_startup = profile.get("current_company_size", "") in ["11-50", "51-200"]
    startup_context_score = 0.0
    if is_startup and 3 <= yoe <= 7:
        startup_context_score = 0.15
    elif is_startup:
        startup_context_score = 0.05
    
    is_consulting = any(firm in current_company for firm in CONSULTING_FIRMS)
    if is_consulting and yoe > 5:
        exp_score *= 0.85

    final = 0.50 * exp_score + 0.35 * ml_relevance + 0.15 * startup_context_score
    final = min(final, 1.0)
    
    return {
        "score": final,
        "reasoning": f"yoe={yoe}({exp_score:.2f}); ml_rel={ml_relevance:.2f}; ml_yoe={ml_relevant_yoe:.1f}yrs"
    }


def score_behavioral(candidate: dict) -> dict:
    signals = candidate.get("redrob_signals", {})
    weights = BEHAVIORAL_WEIGHTS
    parts = {}

    last_active_str = signals.get("last_active_date", "")
    ref = REFERENCE_DATE
    if isinstance(ref, date) and not isinstance(ref, datetime):
        ref_dt = datetime(ref.year, ref.month, ref.day)
    else:
        ref_dt = ref
    
    recency_score = 0.0
    if last_active_str:
        try:
            last_active = datetime.strptime(last_active_str, "%Y-%m-%d")
            days_since = (ref_dt - last_active).days
            if days_since < 7:
                recency_score = 1.0
            elif days_since < 30:
                recency_score = 0.9
            elif days_since < 90:
                recency_score = 0.7
            elif days_since < 180:
                recency_score = 0.4
            else:
                recency_score = max(0.0, 1.0 - days_since / 365)
        except ValueError:
            recency_score = 0.0
    parts["recency"] = recency_score

    parts["open_to_work"] = 1.0 if signals.get("open_to_work_flag") else 0.0

    response_rate = signals.get("recruiter_response_rate", 0.0)
    if response_rate >= 0.8:
        parts["response_rate"] = 1.0
    elif response_rate >= 0.6:
        parts["response_rate"] = 0.8
    elif response_rate >= 0.4:
        parts["response_rate"] = 0.6
    else:
        parts["response_rate"] = response_rate

    rt = signals.get("avg_response_time_hours", 168)
    if rt <= 4:
        parts["response_time"] = 1.0
    elif rt <= 24:
        parts["response_time"] = 0.85
    elif rt <= 72:
        parts["response_time"] = 0.6
    elif rt <= 168:
        parts["response_time"] = 0.3
    else:
        parts["response_time"] = 0.0

    np_days = signals.get("notice_period_days", 90)
    if np_days <= 15:
        parts["notice_period"] = 1.0
    elif np_days <= 30:
        parts["notice_period"] = 0.85
    elif np_days <= 60:
        parts["notice_period"] = 0.6
    elif np_days <= 90:
        parts["notice_period"] = 0.3
    else:
        parts["notice_period"] = 0.0

    completion_rate = signals.get("interview_completion_rate", 0.0)
    if completion_rate >= 0.9:
        parts["interview_completion"] = 1.0
    elif completion_rate >= 0.7:
        parts["interview_completion"] = 0.8
    elif completion_rate >= 0.5:
        parts["interview_completion"] = 0.5
    else:
        parts["interview_completion"] = completion_rate

    v = 0.0
    verify_count = 0
    if signals.get("verified_email"):
        v += 0.35
        verify_count += 1
    if signals.get("verified_phone"):
        v += 0.35
        verify_count += 1
    if signals.get("linkedin_connected"):
        v += 0.30
        verify_count += 1
    parts["verification"] = v

    gh = signals.get("github_activity_score", -1)
    if gh >= 80:
        parts["github"] = 1.0
    elif gh >= 50:
        parts["github"] = 0.8
    elif gh >= 20:
        parts["github"] = 0.5
    elif gh >= 0:
        parts["github"] = gh / 100
    else:
        parts["github"] = 0.0

    views = signals.get("search_appearance_30d", 0)
    saves = signals.get("saved_by_recruiters_30d", 0)
    apps = signals.get("applications_submitted_30d", 0)
    
    view_score = min(views / 200, 1.0) * 0.3
    save_score = min(saves / 20, 1.0) * 0.3
    app_score = min(apps / 10, 1.0) * 0.4
    parts["platform_engagement"] = min(view_score + save_score + app_score, 1.0)

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
            
            sal_mid = (sal_min + sal_max) / 2
            jd_mid = (jd_min + jd_max) / 2
            alignment_score = overlap
            
            if sal_mid < jd_min * 0.7:
                alignment_score *= 0.7
            elif sal_mid > jd_max * 1.5:
                alignment_score *= 0.5
            elif sal_mid > jd_max * 1.3:
                alignment_score *= 0.8
            
            parts["salary_alignment"] = min(alignment_score, 1.0)
        else:
            sal_mid = (sal_min + sal_max) / 2
            if sal_max < jd_min:
                gap = (jd_min - sal_max) / jd_min
                if gap <= 0.2:
                    parts["salary_alignment"] = 0.3
                else:
                    parts["salary_alignment"] = 0.0
            else:
                parts["salary_alignment"] = 0.0
    else:
        parts["salary_alignment"] = 0.0

    underspecified_penalty = 0.0
    missing_signals = sum(1 for k in ["recency", "response_rate", "response_time", "notice_period"] 
                          if parts.get(k, 0) == 0)
    if missing_signals >= 3:
        underspecified_penalty = 0.15

    final = sum(parts.get(k, 0.0) * weights.get(k, 0.0) for k in weights)
    final = max(0.0, final - underspecified_penalty)
    
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

    best_combined = 0.0
    best_is_cs = False
    details = []
    
    applicant_education_scores = []
    
    for edu in education:
        degree = (edu.get("degree") or "").lower().strip()
        field = (edu.get("field_of_study") or "").lower().strip()
        tier = edu.get("tier", "unknown")
        institution = (edu.get("institution") or "").lower().strip()
        grade = edu.get("grade", "")

        degree_score = 0.0
        matched_degree = ""
        for deg_key, dscore in DEGREE_LEVEL_SCORES.items():
            if deg_key.lower() in degree:
                if dscore > degree_score:
                    degree_score = dscore
                    matched_degree = deg_key
        
        tier_score = TIER_SCORES.get(tier, 0.0)
        
        field_cs = any(cs_kw in field for cs_kw in CS_RELATED_FIELDS)
        field_ml_ai = any(ml_kw in field for ml_kw in ["machine learning", "artificial intelligence", "data science"])
        
        field_bonus = 0.0
        if field_ml_ai:
            field_bonus = 0.10
        elif field_cs:
            field_bonus = 0.05
        
        grade_score = 0.0
        if grade:
            try:
                if "cgpa" in grade.lower() or "gpa" in grade.lower():
                    num = float(''.join(c for c in grade if c.isdigit() or c == '.'))
                    if num <= 10:
                        grade_score = min(num / 10, 1.0) * 0.03
                    else:
                        grade_score = min(num / 100, 1.0) * 0.03
                elif "%" in grade:
                    num = float(''.join(c for c in grade if c.isdigit() or c == '.'))
                    grade_score = min(num / 100, 1.0) * 0.03
            except:
                pass
        
        combined = degree_score + tier_score + field_bonus + grade_score
        
        applicant_education_scores.append({
            "combined": combined,
            "degree": degree,
            "field": field,
            "is_cs": field_cs,
            "tier": tier
        })
        
        details.append(
            f"{degree}/{field}/{tier}={degree_score:.2f}+{tier_score:.2f}"
            f"{'+ml' if field_ml_ai else ('+cs' if field_cs else '')}"
        )
    
    if applicant_education_scores:
        scored = sorted(applicant_education_scores, key=lambda x: x["combined"], reverse=True)
        best = scored[0]
        best_combined = best["combined"]
        best_is_cs = best["is_cs"]
        
        for edu in education:
            degree = (edu.get("degree") or "").lower()
            if any(d in degree for d in ["ph.d", "phd"]):
                if best_combined < 0.32:
                    best_combined = max(best_combined, 0.32)
            elif any(d in degree for d in ["m.tech", "mtech", "m.e.", "m.s.", "msc"]):
                for e2 in education:
                    d2 = (e2.get("degree") or "").lower()
                    if any(d in d2 for d in ["b.tech", "btech", "b.e.", "b.sc"]):
                        best_combined = min(best_combined + 0.02, 0.35)

    final = min(best_combined, 0.35)
    return {
        "score": final,
        "reasoning": "; ".join(details)
    }
