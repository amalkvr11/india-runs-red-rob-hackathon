from datetime import datetime, date
from config import HONEYPOT_THRESHOLDS, REFERENCE_DATE, HONEYPOT_FUTURE_ACTIVITY_DAYS, HONEYPOT_MAX_YOE, HONEYPOT_MIN_PROFILE_COMPLETENESS, HONEYPOT_SKILL_COUNT_UNREALISTIC, HONEYPOT_ASSESSMENT_MIN_SCORE, HONEYPOT_MAX_REASONABLE_CAREERS


def detect_honeypot(candidate: dict) -> dict:
    signals = candidate.get("redrob_signals", {})
    skills = candidate.get("skills", [])
    profile = candidate.get("profile", {})
    history = candidate.get("career_history", [])
    flags = []
    severity = 0.0

    thresholds = HONEYPOT_THRESHOLDS

    expert_skills = [s for s in skills if s.get("proficiency", "").lower() == "expert"]
    advanced_skills = [s for s in skills if s.get("proficiency", "").lower() == "advanced"]
    
    if len(expert_skills) > thresholds["expert_skill_count_threshold"]:
        avg_endorsements = (
            sum(s.get("endorsements", 0) for s in expert_skills) / len(expert_skills)
            if expert_skills else 0
        )
        avg_duration = (
            sum(s.get("duration_months", 0) for s in expert_skills) / len(expert_skills)
            if expert_skills else 0
        )
        
        if avg_endorsements < thresholds["expert_low_endorsement_avg"]:
            flags.append("many_expert_low_endorsement")
            severity += 0.20
        
        if avg_duration < thresholds["expert_min_duration_months"]:
            flags.append("expert_skills_short_avg_duration")
            severity += 0.10

    if len(expert_skills) > thresholds["max_reasonable_expert_skills"]:
        flags.append("excessive_expert_skills")
        severity += 0.25

    for s in expert_skills:
        dur = s.get("duration_months", 0)
        endorsements = s.get("endorsements", 0)
        if dur < thresholds["expert_min_duration_months"] and endorsements < 3:
            flags.append("expert_short_duration_no_endorse")
            severity += 0.15
            break  

    claimed_yoe = profile.get("years_of_experience", 0)
    history_months = sum(
        e.get("duration_months", 0) for e in history
    )
    history_yoe = history_months / 12
    
    yoe_gap = claimed_yoe - history_yoe
    if yoe_gap > thresholds["yoe_career_gap_months"] / 12:
        gap_ratio = yoe_gap / max(claimed_yoe, 1)
        if gap_ratio > 0.6:
            flags.append(f"yoe_career_mismatch_severe:{yoe_gap:.1f}yrs")
            severity += 0.35
        elif gap_ratio > 0.4:
            flags.append(f"yoe_career_mismatch:{yoe_gap:.1f}yrs")
            severity += 0.25
        else:
            flags.append(f"yoe_career_mismatch_minor:{yoe_gap:.1f}yrs")
            severity += 0.15

    assessment_scores = signals.get("skill_assessment_scores", {})
    contradiction_count = 0
    for s in skills:
        prof = s.get("proficiency", "").lower()
        if prof in ("expert", "advanced"):
            name = s.get("name", "")
            score = assessment_scores.get(name)
            if score is not None and score < thresholds["assessment_contradiction_threshold"]:
                contradiction_count += 1
    
    if contradiction_count >= 3:
        flags.append(f"multiple_assessment_contradictions:{contradiction_count}")
        severity += 0.25
    elif contradiction_count >= 1:
        flags.append(f"assessment_contradiction:{contradiction_count}")
        severity += 0.12

    completeness = signals.get("profile_completeness_score", 0)
    if completeness < HONEYPOT_MIN_PROFILE_COMPLETENESS:
        flags.append("low_profile_completeness")
        severity += 0.12

    last_active_str = signals.get("last_active_date", "")
    if last_active_str:
        try:
            last_active = datetime.strptime(last_active_str, "%Y-%m-%d").date()
            ref = REFERENCE_DATE
            if isinstance(ref, datetime):
                ref = ref.date()
            days_ahead = (last_active - ref).days
            if days_ahead > HONEYPOT_FUTURE_ACTIVITY_DAYS * 2:
                flags.append(f"future_activity_severe:{days_ahead}d_ahead")
                severity += 0.40
            elif days_ahead > HONEYPOT_FUTURE_ACTIVITY_DAYS:
                flags.append(f"future_activity:{days_ahead}d_ahead")
                severity += 0.25
        except ValueError:
            pass

    if claimed_yoe > HONEYPOT_MAX_YOE:
        flags.append(f"unrealistic_yoe:{claimed_yoe}")
        severity += 0.30
    elif claimed_yoe > 40:
        flags.append(f"suspicious_yoe:{claimed_yoe}")
        severity += 0.15

    if len(skills) > HONEYPOT_SKILL_COUNT_UNREALISTIC:
        flags.append(f"excessive_skills:{len(skills)}")
        severity += 0.20
    elif len(skills) > 25:
        if len(expert_skills) > 10:
            flags.append(f"many_skills_many_expert:{len(skills)},{len(expert_skills)}")
            severity += 0.15

    if assessment_scores:
        all_zero = all(score == 0 for score in assessment_scores.values() if score is not None)
        if all_zero and len(assessment_scores) > 3:
            flags.append("all_assessments_zero")
            severity += 0.25
        else:
            all_low = all(
                score is not None and score < HONEYPOT_ASSESSMENT_MIN_SCORE
                for score in assessment_scores.values()
            )
            if all_low and len(assessment_scores) > 3:
                flags.append("all_assessments_very_low")
                severity += 0.15

    career_count = len(history)
    if career_count > HONEYPOT_MAX_REASONABLE_CAREERS:
        flags.append(f"excessive_careers:{career_count}")
        severity += 0.20
    
    if career_count >= 3:
        companies = [e.get("company", "") for e in history]
        durations = [e.get("duration_months", 0) for e in history]
        if len(set(companies)) == 1 and max(durations) < 24:
            flags.append("frequent_job_hops_same_company")
            severity += 0.08

    required_fields = ["current_title", "years_of_experience", "location"]
    missing = [f for f in required_fields if not profile.get(f)]
    if len(missing) >= 2:
        flags.append(f"missing_fields:{','.join(missing)}")
        severity += 0.15
    
    current_title = (profile.get("current_title") or "").lower()
    if current_title and all(kw in current_title for kw in ["senior", "junior"]):
        flags.append("contradictory_title")
        severity += 0.15
    
    if history:
        titles = [(e.get("start_date", ""), e.get("title", "")) for e in history]
        titles.sort()
        for i in range(1, len(titles)):
            prev_title = titles[i-1][1].lower()
            curr_title = titles[i][1].lower()
            if "senior" in prev_title and "junior" in curr_title:
                flags.append("regressing_career_trajectory")
                severity += 0.10
                break
    
    summary = (profile.get("summary") or "").lower()
    statement = (profile.get("statement") or "").lower()
    combined_text = f"{summary} {statement}"
    
    repetitive_phrases = [
        "professional with",
        "years of experience",
        "curious about how ai",
        "experimented with chatgpt",
    ]
    phrase_count = sum(1 for phrase in repetitive_phrases if phrase in combined_text)
    if phrase_count >= 3:
        flags.append(f"template_like_summary:{phrase_count}")
        severity += 0.15
    
    total_endorsements = sum(s.get("endorsements", 0) for s in skills)
    if len(skills) > 15 and total_endorsements < 10:
        flags.append(f"many_skills_low_endorsements:{len(skills)},{total_endorsements}")
        severity += 0.12

    penalty = min(severity, 0.75)
    return {
        "penalty": penalty,
        "flags": flags,
        "is_honeypot": penalty > 0.15,
    }
