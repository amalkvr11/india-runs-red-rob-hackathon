from datetime import datetime, date
from config import HONEYPOT_THRESHOLDS, REFERENCE_DATE, HONEYPOT_FUTURE_ACTIVITY_DAYS, HONEYPOT_MAX_YOE, HONEYPOT_MIN_PROFILE_COMPLETENESS, HONEYPOT_SKILL_COUNT_UNREALISTIC, HONEYPOT_ASSESSMENT_MIN_SCORE, HONEYPOT_MAX_REASONABLE_CAREERS


def detect_honeypot(candidate: dict) -> dict:
    signals = candidate.get("redrob_signals", {})
    skills = candidate.get("skills", [])
    profile = candidate.get("profile", {})
    flags = []
    severity = 0.0

    thresholds = HONEYPOT_THRESHOLDS

    # 1. Too many expert skills with low endorsements
    expert_skills = [s for s in skills if s.get("proficiency", "").lower() == "expert"]
    if len(expert_skills) > thresholds["expert_skill_count_threshold"]:
        avg_endorsements = (
            sum(s.get("endorsements", 0) for s in expert_skills) / len(expert_skills)
            if expert_skills else 0
        )
        if avg_endorsements < thresholds["expert_low_endorsement_avg"]:
            flags.append("many_expert_low_endorsement")
            severity += 0.15

    # 2. Too many expert skills overall
    if len(expert_skills) > thresholds["max_reasonable_expert_skills"]:
        flags.append("excessive_expert_skills")
        severity += 0.15

    # 3. Expert skills with very short duration
    for s in expert_skills:
        dur = s.get("duration_months", 0)
        if dur < thresholds["expert_min_duration_months"]:
            flags.append("expert_short_duration")
            severity += 0.05
            break

    # 4. YOE gap: claimed > career history total
    claimed_yoe = profile.get("years_of_experience", 0)
    history_months = sum(
        e.get("duration_months", 0) for e in candidate.get("career_history", [])
    )
    history_yoe = history_months / 12
    if claimed_yoe - history_yoe > thresholds["yoe_career_gap_months"] / 12:
        flags.append("yoe_career_mismatch")
        severity += 0.20

    # 5. Assessment contradiction: expert/advanced with low assessment score
    assessment_scores = signals.get("skill_assessment_scores", {})
    for s in skills:
        prof = s.get("proficiency", "").lower()
        if prof in ("expert", "advanced"):
            name = s.get("name", "")
            score = assessment_scores.get(name)
            if score is not None and score < thresholds["assessment_contradiction_threshold"]:
                flags.append(f"assessment_contradiction:{name}={score}")
                severity += 0.15
                break

    # 6. Profile completeness very low
    completeness = signals.get("profile_completeness_score", 0)
    if completeness < HONEYPOT_MIN_PROFILE_COMPLETENESS:
        flags.append("low_profile_completeness")
        severity += 0.10

    # 7. Future last_active_date
    last_active_str = signals.get("last_active_date", "")
    if last_active_str:
        try:
            last_active = datetime.strptime(last_active_str, "%Y-%m-%d").date()
            ref = REFERENCE_DATE
            if isinstance(ref, datetime):
                ref = ref.date()
            days_ahead = (last_active - ref).days
            if days_ahead > HONEYPOT_FUTURE_ACTIVITY_DAYS:
                flags.append(f"future_activity:{days_ahead}d_ahead")
                severity += 0.25
        except ValueError:
            pass

    # 8. Unrealistic years of experience
    if claimed_yoe > HONEYPOT_MAX_YOE:
        flags.append(f"unrealistic_yoe:{claimed_yoe}")
        severity += 0.20

    # 9. Too many skills (likely script-generated)
    if len(skills) > HONEYPOT_SKILL_COUNT_UNREALISTIC:
        flags.append(f"excessive_skills:{len(skills)}")
        severity += 0.10

    # 10. All assessment scores are suspiciously low/zero
    if assessment_scores:
        all_low = all(
            score is not None and score < HONEYPOT_ASSESSMENT_MIN_SCORE
            for score in assessment_scores.values()
        )
        if all_low and len(assessment_scores) > 3:
            flags.append("all_assessments_very_low")
            severity += 0.10

    # 11. Too many career entries (script-generated)
    career_count = len(candidate.get("career_history", []))
    if career_count > HONEYPOT_MAX_REASONABLE_CAREERS:
        flags.append(f"excessive_careers:{career_count}")
        severity += 0.15

    # 12. Missing all required profile fields
    required_fields = ["current_title", "years_of_experience", "location"]
    missing = [f for f in required_fields if not profile.get(f)]
    if len(missing) >= 2:
        flags.append(f"missing_fields:{','.join(missing)}")
        severity += 0.10

    penalty = min(severity, 0.6)
    return {
        "penalty": penalty,
        "flags": flags,
        "is_honeypot": penalty > 0.12,
    }
