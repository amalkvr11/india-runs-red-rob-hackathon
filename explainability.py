"""
explainability.py - SHAP-based feature importance and candidate explanation.

Provides:
1. Feature importance analysis across all scorers
2. Individual candidate explanations (why did they get this rank?)
3. Counterfactual explanations (what would change their rank?)
"""

import json
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class ShapExplainer:
    """
    SHAP-inspired explainability for candidate rankings.
    
    Since we're using a weighted sum of scorers (not ML model),
    we compute "attribution" as each scorer's contribution to final score.
    """
    
    def __init__(self):
        self.scorer_names = [
            "title_role", "skills", "career_quality", "experience",
            "statement", "behavioral", "location", "education"
        ]
    
    def explain_candidate(self, candidate: dict, 
                         sub_scores: Dict,
                         final_score: float,
                         honeypot_penalty: float) -> Dict:
        """
        Generate detailed explanation for a candidate's score.
        
        Returns:
            Dict with feature importance, contributions, and insights
        """
        from config import SCORER_WEIGHTS
        
        contributions = {}
        weighted_contributions = {}
        
        # Calculate weighted contribution of each scorer
        total_before_penalty = 0.0
        for name in self.scorer_names:
            score = sub_scores.get(name, 0.0)
            weight = SCORER_WEIGHTS.get(name, 0.0)
            weighted = score * weight
            
            contributions[name] = {
                "raw_score": round(score, 4),
                "weight": weight,
                "weighted_score": round(weighted, 4),
                "percentage": round(weighted * 100, 2) if final_score > 0 else 0
            }
            
            weighted_contributions[name] = weighted
            total_before_penalty += weighted
        
        # Calculate honeypot impact
        honeypot_impact = total_before_penalty * honeypot_penalty
        
        # Determine strengths and weaknesses
        sorted_contribs = sorted(weighted_contributions.items(), 
                               key=lambda x: x[1], reverse=True)
        
        strengths = []
        weaknesses = []
        
        for name, contrib in sorted_contribs[:3]:
            if contrib > 0.05:  # Significant contribution
                strengths.append({
                    "dimension": name,
                    "score": sub_scores.get(name, 0.0),
                    "contribution": round(contrib, 4),
                    "explanation": self._get_strength_explanation(name, sub_scores.get(name, 0.0))
                })
        
        for name, contrib in sorted_contribs[-3:]:
            if contrib < 0.05:  # Low contribution
                weaknesses.append({
                    "dimension": name,
                    "score": sub_scores.get(name, 0.0),
                    "contribution": round(contrib, 4),
                    "explanation": self._get_weakness_explanation(name, sub_scores.get(name, 0.0))
                })
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            candidate, sub_scores, strengths, weaknesses
        )
        
        return {
            "candidate_id": candidate.get("candidate_id", "unknown"),
            "final_score": round(final_score, 4),
            "score_before_penalty": round(total_before_penalty, 4),
            "honeypot_penalty": round(honeypot_penalty, 4),
            "honeypot_impact": round(honeypot_impact, 4),
            "contributions": contributions,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "top_strength": strengths[0] if strengths else None,
            "main_weakness": weaknesses[0] if weaknesses else None,
            "recommendations": recommendations,
            "summary": self._generate_summary(candidate, final_score, strengths, weaknesses)
        }
    
    def _get_strength_explanation(self, dimension: str, score: float) -> str:
        """Generate human-readable explanation for a strength."""
        explanations = {
            "title_role": {
                (0.9, 1.0): "Perfect title match - directly relevant to role",
                (0.7, 0.9): "Strong title alignment with ML engineering",
                (0.5, 0.7): "Good title with adjacent ML experience"
            },
            "skills": {
                (0.9, 1.0): "Exceptional skill coverage in core ML areas",
                (0.7, 0.9): "Strong skill set matching job requirements",
                (0.5, 0.7): "Good skills with some relevant tools"
            },
            "career_quality": {
                (0.7, 1.0): "Excellent career trajectory with ML focus",
                (0.5, 0.7): "Solid career progression with relevant experience"
            },
            "experience": {
                (0.8, 1.0): "Ideal years of experience in ML roles",
                (0.6, 0.8): "Good ML experience at appropriate level"
            },
            "statement": {
                (0.5, 1.0): "Strong statement showing ML passion and intent"
            },
            "behavioral": {
                (0.7, 1.0): "Highly responsive and engaged candidate"
            },
            "location": {
                (0.8, 1.0): "Ideally located for role"
            },
            "education": {
                (0.3, 0.5): "Strong educational background in relevant field"
            }
        }
        
        if dimension in explanations:
            for (low, high), text in explanations[dimension].items():
                if low <= score <= high:
                    return text
        
        return f"Score: {score:.2f}"
    
    def _get_weakness_explanation(self, dimension: str, score: float) -> str:
        """Generate human-readable explanation for a weakness."""
        explanations = {
            "title_role": {
                (0.0, 0.3): "Title does not align with ML engineering",
                (0.3, 0.5): "Title is adjacent but not focused on ML"
            },
            "skills": {
                (0.0, 0.3): "Limited relevant ML skills",
                (0.3, 0.5): "Skills not aligned with core requirements"
            },
            "career_quality": {
                (0.0, 0.3): "Limited ML career history"
            },
            "experience": {
                (0.0, 0.4): "Insufficient ML experience for senior role"
            },
            "statement": {
                (0.0, 0.2): "No clear ML intent in statement"
            },
            "behavioral": {
                (0.0, 0.4): "Low engagement signals"
            }
        }
        
        if dimension in explanations:
            for (low, high), text in explanations[dimension].items():
                if low <= score <= high:
                    return text
        
        return f"Score: {score:.2f}"
    
    def _generate_recommendations(self, candidate: dict, 
                                 sub_scores: Dict,
                                 strengths: List,
                                 weaknesses: List) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Score-based recommendations
        final_score = sum(sub_scores.values()) / len(sub_scores) if sub_scores else 0
        
        if final_score >= 0.8:
            recommendations.append("Strong candidate - prioritize for immediate outreach")
        elif final_score >= 0.6:
            recommendations.append("Good candidate - worth interviewing")
        elif final_score >= 0.4:
            recommendations.append("Consider for junior role or further screening")
        else:
            recommendations.append("Not recommended for this position")
        
        # Dimension-specific recommendations
        if sub_scores.get("behavioral", 0) < 0.3:
            recommendations.append("Low engagement - may not respond to outreach")
        
        if sub_scores.get("location", 0) < 0.5:
            recommendations.append("Remote work or relocation package may be needed")
        
        # Honeypot check
        if candidate.get("honeypot", {}).get("is_honeypot"):
            flags = candidate.get("honeypot", {}).get("flags", [])
            recommendations.append(f"⚠️ Potential fake profile: {', '.join(flags[:2])}")
        
        return recommendations
    
    def _generate_summary(self, candidate: dict, 
                         final_score: float,
                         strengths: List,
                         weaknesses: List) -> str:
        """Generate a one-line summary."""
        profile = candidate.get("profile", {})
        title = profile.get("current_title", "Unknown")
        
        if final_score >= 0.8:
            quality = "excellent"
        elif final_score >= 0.6:
            quality = "good"
        elif final_score >= 0.4:
            quality = "moderate"
        else:
            quality = "poor"
        
        top_strength = strengths[0]["dimension"] if strengths else "N/A"
        
        return (f"{title} candidate with {quality} overall fit. "
                f"Strongest in {top_strength}. Score: {final_score:.2f}")
    
    def compute_feature_importance(self, candidates: List[Dict]) -> Dict:
        """
        Compute global feature importance across all candidates.
        
        Returns which dimensions have most impact on rankings.
        """
        from config import SCORER_WEIGHTS
        
        importance = {name: [] for name in self.scorer_names}
        
        for candidate in candidates:
            sub_scores = candidate.get("sub_scores", {})
            
            for name in self.scorer_names:
                score = sub_scores.get(name, 0.0)
                weight = SCORER_WEIGHTS.get(name, 0.0)
                importance[name].append(score * weight)
        
        # Compute statistics
        results = {}
        for name, values in importance.items():
            if values:
                results[name] = {
                    "mean": round(np.mean(values), 4),
                    "std": round(np.std(values), 4),
                    "median": round(np.median(values), 4),
                    "max": round(np.max(values), 4),
                    "min": round(np.min(values), 4),
                    "importance_score": round(np.mean(values) / (np.std(values) + 0.001), 4)
                }
        
        # Sort by importance
        sorted_results = sorted(results.items(), 
                              key=lambda x: x[1]["importance_score"], 
                              reverse=True)
        
        return {
            "by_dimension": results,
            "ranking": [name for name, _ in sorted_results],
            "top_3": [name for name, _ in sorted_results[:3]],
            "bottom_3": [name for name, _ in sorted_results[-3:]]
        }
    
    def generate_counterfactual(self, candidate: dict,
                                target_rank: int,
                                current_results: List[Dict]) -> Dict:
        """
        Generate counterfactual: what would change to reach target rank?
        
        Args:
            candidate: The candidate to analyze
            target_rank: Desired rank (e.g., 10 for top 10)
            current_results: Full ranking results
        
        Returns:
            Dict with counterfactual analysis
        """
        if not current_results or len(current_results) < target_rank:
            return {"error": "Not enough results"}
        
        current_score = candidate.get("score", 0)
        target_score = current_results[target_rank - 1]["score"]
        score_gap = target_score - current_score
        
        if score_gap <= 0:
            return {
                "message": "Already at or above target rank",
                "current_rank": self._find_rank(candidate, current_results),
                "target_rank": target_rank
            }
        
        sub_scores = candidate.get("sub_scores", {})
        
        # Calculate required improvements
        improvements = []
        
        # Option 1: Improve title
        if sub_scores.get("title_role", 0) < 1.0:
            current_title_score = sub_scores.get("title_role", 0)
            gap_to_close = score_gap / 0.20  # title_role weight is 0.20
            new_title_score = min(1.0, current_title_score + gap_to_close)
            improvements.append({
                "dimension": "title_role",
                "current": round(current_title_score, 3),
                "target": round(new_title_score, 3),
                "impact": round((new_title_score - current_title_score) * 0.20, 4),
                "action": "Promote to senior ML title or gain ML-focused role"
            })
        
        # Option 2: Improve skills
        if sub_scores.get("skills", 0) < 1.0:
            current_skill_score = sub_scores.get("skills", 0)
            gap_to_close = score_gap / 0.22
            new_skill_score = min(1.0, current_skill_score + gap_to_close)
            improvements.append({
                "dimension": "skills",
                "current": round(current_skill_score, 3),
                "target": round(new_skill_score, 3),
                "impact": round((new_skill_score - current_skill_score) * 0.22, 4),
                "action": "Add core ML skills: vector DBs, embeddings, LLMs"
            })
        
        # Option 3: Reduce honeypot flags
        honeypot = candidate.get("honeypot", {})
        if honeypot.get("is_honeypot"):
            penalty = honeypot.get("penalty", 0)
            improvements.append({
                "dimension": "honeypot",
                "current": round(penalty, 3),
                "target": 0.0,
                "impact": round(current_score * penalty / (1 - penalty), 4),
                "action": "Remove suspicious profile indicators"
            })
        
        # Sort by impact
        improvements.sort(key=lambda x: x.get("impact", 0), reverse=True)
        
        return {
            "candidate_id": candidate.get("candidate_id"),
            "current_score": round(current_score, 4),
            "target_score": round(target_score, 4),
            "score_gap": round(score_gap, 4),
            "current_rank": self._find_rank(candidate, current_results),
            "target_rank": target_rank,
            "required_improvements": improvements[:3],
            "easiest_path": improvements[0] if improvements else None
        }
    
    def _find_rank(self, candidate: dict, results: List[Dict]) -> int:
        """Find current rank of candidate."""
        cid = candidate.get("candidate_id")
        for i, r in enumerate(results):
            if r.get("candidate_id") == cid:
                return i + 1
        return -1
    
    def export_explanations(self, results: List[Dict], 
                           output_path: str = "explanations.json"):
        """Export detailed explanations for all candidates."""
        explanations = []
        
        for result in results[:100]:  # Top 100
            exp = self.explain_candidate(
                result,
                result.get("sub_scores", {}),
                result.get("score", 0),
                result.get("honeypot", {}).get("penalty", 0)
            )
            explanations.append(exp)
        
        with open(output_path, "w") as f:
            json.dump(explanations, f, indent=2)
        
        logger.info(f"Exported {len(explanations)} explanations to {output_path}")


def explain_top_candidates(results: List[Dict], n: int = 10) -> List[Dict]:
    """Generate explanations for top N candidates."""
    explainer = ShapExplainer()
    explanations = []
    
    for result in results[:n]:
        exp = explainer.explain_candidate(
            result,
            result.get("sub_scores", {}),
            result.get("score", 0),
            result.get("honeypot", {}).get("penalty", 0)
        )
        explanations.append(exp)
    
    return explanations


def print_candidate_explanation(explanation: Dict):
    """Pretty print a candidate explanation."""
    print("\n" + "="*70)
    print(f"Candidate: {explanation['candidate_id']}")
    print(f"Final Score: {explanation['final_score']:.4f}")
    print(f"Score Before Penalty: {explanation['score_before_penalty']:.4f}")
    print(f"Honeypot Penalty: {explanation['honeypot_penalty']:.4f}")
    print("="*70)
    
    print("\n📊 DIMENSION CONTRIBUTIONS:")
    for name, contrib in explanation['contributions'].items():
        bar = "█" * int(contrib['percentage'] / 5)
        print(f"  {name:20s}: {bar:20s} {contrib['weighted_score']:.4f} ({contrib['percentage']:.1f}%)")
    
    print("\n✅ TOP STRENGTHS:")
    for s in explanation['strengths'][:3]:
        print(f"  • {s['dimension']:20s}: {s['explanation']}")
    
    print("\n⚠️  AREAS FOR IMPROVEMENT:")
    for w in explanation['weaknesses'][:2]:
        print(f"  • {w['dimension']:20s}: {w['explanation']}")
    
    print("\n💡 RECOMMENDATIONS:")
    for rec in explanation['recommendations']:
        print(f"  • {rec}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test with sample candidate
    test_candidate = {
        "candidate_id": "TEST_001",
        "score": 0.75,
        "sub_scores": {
            "title_role": 1.0,
            "skills": 0.85,
            "career_quality": 0.65,
            "experience": 0.80,
            "statement": 0.55,
            "behavioral": 0.70,
            "location": 1.0,
            "education": 0.30
        },
        "honeypot": {"penalty": 0.0, "is_honeypot": False},
        "profile": {"current_title": "Senior ML Engineer"}
    }
    
    explainer = ShapExplainer()
    explanation = explainer.explain_candidate(
        test_candidate,
        test_candidate["sub_scores"],
        test_candidate["score"],
        0.0
    )
    
    print_candidate_explanation(explanation)
