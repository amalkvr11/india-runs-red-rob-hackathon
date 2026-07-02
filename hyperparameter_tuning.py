"""
hyperparameter_tuning.py - Automated weight optimization for scoring dimensions.

Uses Bayesian optimization (Optuna) to find optimal scorer weights based on 
validation metrics.
"""

import json
import logging
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

# Ground truth labels for validation
# These would ideally come from manual labeling or historical hiring data
VALIDATION_LABELS = {
    # candidate_id -> (label, ideal_rank)
    # Label: 1.0 = ideal hire, 0.5 = maybe, 0.0 = reject
    "CAND_0010685": (1.0, 1),   # NLP Engineer - excellent
    "CAND_0046064": (1.0, 2),   # Senior NLP Engineer - excellent
    "CAND_0005260": (1.0, 3),   # Senior NLP Engineer - excellent
    "CAND_0016163": (1.0, 5),   # Applied ML Engineer - excellent
    "CAND_0010257": (0.9, 10),  # Senior Data Scientist - very good
    "CAND_0043228": (1.0, 6),   # Applied ML Engineer - excellent
    "CAND_0083879": (1.0, 7),   # ML Engineer - excellent
    "CAND_0006418": (0.9, 8),   # ML Engineer - very good
    "CAND_0064904": (1.0, 9),   # AI Engineer - excellent
    "CAND_0015528": (0.95, 11), # Applied ML Engineer - excellent
    "CAND_0058575": (0.9, 12),  # AI Engineer - very good
    "CAND_0092255": (0.9, 13),  # ML Engineer - very good
    "CAND_0027691": (0.85, 14), # NLP Engineer - good
    "CAND_0076831": (0.85, 15), # Search Engineer - good
    "CAND_0055905": (0.85, 16), # Senior ML Engineer - good
    # Add poor candidates with low labels
    "CAND_0004989": (0.0, 1000),  # HR Manager - reject
    "CAND_0001195": (0.0, 1001),  # HR Manager - reject
    "CAND_0000339": (0.1, 998),   # Content Writer - poor fit
    "CAND_0001082": (0.0, 999),   # HR Manager - reject
    "CAND_0001218": (0.1, 997),   # Graphic Designer - poor fit
}


@dataclass
class OptimizationConfig:
    """Configuration for hyperparameter optimization."""
    n_trials: int = 100
    timeout: int = 3600  # 1 hour max
    metric: str = "ndcg"  # "ndcg", "precision", "recall", "mae"
    min_weight: float = 0.01
    max_weight: float = 0.40
    weight_sum_tolerance: float = 0.001


class WeightOptimizer:
    """Bayesian optimization for scorer weights using Optuna."""
    
    def __init__(self, config: Optional[OptimizationConfig] = None):
        self.config = config or OptimizationConfig()
        self.best_weights = None
        self.best_score = -np.inf
        
    def load_candidate_data(self, candidates_path: str, 
                           labels: Optional[Dict] = None) -> List[Dict]:
        """Load candidates and attach labels."""
        from ranker import load_candidates
        
        candidates = load_candidates(candidates_path)
        labels = labels or VALIDATION_LABELS
        
        # Attach labels
        for c in candidates:
            cid = c.get("candidate_id", "")
            if cid in labels:
                c["label"] = labels[cid][0]
                c["ideal_rank"] = labels[cid][1]
            else:
                # Default: no label
                c["label"] = None
                c["ideal_rank"] = None
        
        # Filter to only labeled candidates for optimization
        labeled = [c for c in candidates if c.get("label") is not None]
        logger.info(f"Loaded {len(labeled)} labeled candidates for optimization")
        
        return labeled
    
    def _compute_ndcg(self, candidates: List[Dict], k: int = 10) -> float:
        """Compute NDCG@k ranking metric."""
        # Sort by score descending
        sorted_candidates = sorted(candidates, 
                                   key=lambda x: x.get("current_score", 0), 
                                   reverse=True)
        
        # Compute DCG
        dcg = 0.0
        for i, c in enumerate(sorted_candidates[:k]):
            label = c.get("label", 0.0)
            # Gain increases with label, position discount
            dcg += (2 ** label - 1) / np.log2(i + 2)
        
        # Compute ideal DCG
        ideal_labels = sorted([c.get("label", 0.0) for c in candidates], 
                            reverse=True)
        idcg = 0.0
        for i, label in enumerate(ideal_labels[:k]):
            idcg += (2 ** label - 1) / np.log2(i + 2)
        
        return dcg / idcg if idcg > 0 else 0.0
    
    def _compute_precision_at_k(self, candidates: List[Dict], 
                                 k: int = 10, threshold: float = 0.5) -> float:
        """Compute Precision@k."""
        sorted_candidates = sorted(candidates, 
                                   key=lambda x: x.get("current_score", 0), 
                                   reverse=True)
        
        top_k = sorted_candidates[:k]
        relevant = sum(1 for c in top_k if c.get("label", 0.0) >= threshold)
        
        return relevant / k
    
    def _compute_rank_correlation(self, candidates: List[Dict]) -> float:
        """Compute Spearman correlation between predicted and ideal ranks."""
        from scipy.stats import spearmanr
        
        # Get candidates with ideal ranks
        ranked = [c for c in candidates if c.get("ideal_rank") is not None]
        
        if len(ranked) < 3:
            return 0.0
        
        # Sort by predicted score
        sorted_candidates = sorted(ranked, 
                                   key=lambda x: x.get("current_score", 0), 
                                   reverse=True)
        
        # Assign predicted ranks
        predicted_ranks = {c["candidate_id"]: i+1 
                         for i, c in enumerate(sorted_candidates)}
        
        # Get rank lists
        pred_ranks = [predicted_ranks.get(c["candidate_id"], 9999) 
                     for c in ranked]
        ideal_ranks = [c["ideal_rank"] for c in ranked]
        
        # Compute correlation
        corr, _ = spearmanr(pred_ranks, ideal_ranks)
        
        return corr if not np.isnan(corr) else 0.0
    
    def objective(self, trial, candidates: List[Dict], 
                  scorer_functions: Dict) -> float:
        """
        Objective function for Optuna optimization.
        
        Returns the score to maximize.
        """
        try:
            import optuna
        except ImportError:
            logger.error("Optuna not installed. Using random search.")
            return self._objective_random(candidates, scorer_functions)
        
        # Suggest weights that sum to 1.0
        # Use Dirichlet distribution for natural simplex sampling
        weights = {}
        
        # Sample raw weights
        raw_weights = []
        for name in scorer_functions.keys():
            # Log-uniform sampling for better exploration
            w = trial.suggest_float(f"weight_{name}", 
                                   self.config.min_weight,
                                   self.config.max_weight,
                                   log=True)
            raw_weights.append(w)
        
        # Normalize to sum to 1.0
        total = sum(raw_weights)
        for i, name in enumerate(scorer_functions.keys()):
            weights[name] = raw_weights[i] / total
        
        # Evaluate with these weights
        score = self._evaluate_weights(candidates, scorer_functions, weights)
        
        return score
    
    def _objective_random(self, candidates: List[Dict], 
                         scorer_functions: Dict) -> float:
        """Fallback random search if Optuna not available."""
        import random
        
        weights = {}
        raw = [random.random() for _ in scorer_functions]
        total = sum(raw)
        for i, name in enumerate(scorer_functions.keys()):
            weights[name] = raw[i] / total
        
        return self._evaluate_weights(candidates, scorer_functions, weights)
    
    def _evaluate_weights(self, candidates: List[Dict], 
                         scorer_functions: Dict,
                         weights: Dict) -> float:
        """Evaluate a set of weights on the validation set."""
        from honeypot import detect_honeypot
        
        # Score all candidates with these weights
        for candidate in candidates:
            sub_scores = {}
            
            # Compute sub-scores
            for name, func in scorer_functions.items():
                try:
                    result = func(candidate)
                    sub_scores[name] = result["score"]
                except Exception as e:
                    logger.error(f"Error in scorer {name}: {e}")
                    sub_scores[name] = 0.0
            
            # Apply weights
            weighted_sum = sum(sub_scores[name] * weights.get(name, 0) 
                             for name in sub_scores)
            
            # Apply honeypot penalty
            honeypot = detect_honeypot(candidate)
            penalty = honeypot.get("penalty", 0)
            final_score = weighted_sum * (1 - penalty)
            
            candidate["current_score"] = final_score
            candidate["sub_scores"] = sub_scores
        
        # Compute metrics
        if self.config.metric == "ndcg":
            return self._compute_ndcg(candidates, k=10)
        elif self.config.metric == "precision":
            return self._compute_precision_at_k(candidates, k=10)
        elif self.config.metric == "rank_corr":
            return self._compute_rank_correlation(candidates)
        else:
            # Combined metric
            ndcg = self._compute_ndcg(candidates, k=10)
            prec = self._compute_precision_at_k(candidates, k=10)
            corr = self._compute_rank_correlation(candidates)
            return 0.5 * ndcg + 0.3 * prec + 0.2 * corr
    
    def optimize(self, candidates_path: str, 
                 scorer_functions: Dict,
                 labels: Optional[Dict] = None) -> Dict:
        """
        Run hyperparameter optimization.
        
        Returns dict with best weights and metrics.
        """
        try:
            import optuna
            has_optuna = True
        except ImportError:
            has_optuna = False
            logger.warning("Optuna not installed. Using random search.")
        
        # Load candidates
        candidates = self.load_candidate_data(candidates_path, labels)
        
        if len(candidates) < 5:
            logger.error("Not enough labeled candidates for optimization")
            return None
        
        logger.info(f"Starting optimization with {self.config.n_trials} trials")
        logger.info(f"Metric: {self.config.metric}")
        logger.info(f"Candidates: {len(candidates)}")
        
        if has_optuna:
            # Use Optuna for Bayesian optimization
            study = optuna.create_study(direction="maximize")
            
            def objective_wrapper(trial):
                return self.objective(trial, candidates, scorer_functions)
            
            study.optimize(objective_wrapper, 
                          n_trials=self.config.n_trials,
                          timeout=self.config.timeout,
                          show_progress_bar=True)
            
            self.best_weights = study.best_params
            self.best_score = study.best_value
            
            # Normalize weights from best trial
            raw = [self.best_weights[f"weight_{name}"] 
                  for name in scorer_functions.keys()]
            total = sum(raw)
            normalized = {name: raw[i]/total 
                        for i, name in enumerate(scorer_functions.keys())}
            
            logger.info(f"Best score: {self.best_score:.4f}")
            logger.info(f"Best weights: {normalized}")
            
            return {
                "best_weights": normalized,
                "best_score": self.best_score,
                "n_trials": len(study.trials),
                "metric": self.config.metric
            }
        else:
            # Random search fallback
            return self._random_search(candidates, scorer_functions)
    
    def _random_search(self, candidates: List[Dict], 
                      scorer_functions: Dict) -> Dict:
        """Fallback random search."""
        import random
        
        best_score = -np.inf
        best_weights = None
        
        for i in range(self.config.n_trials):
            weights = {}
            raw = [random.random() for _ in scorer_functions]
            total = sum(raw)
            for j, name in enumerate(scorer_functions.keys()):
                weights[name] = raw[j] / total
            
            score = self._evaluate_weights(candidates, scorer_functions, weights)
            
            if score > best_score:
                best_score = score
                best_weights = weights
            
            if (i + 1) % 10 == 0:
                logger.info(f"Trial {i+1}/{self.config.n_trials}: best={best_score:.4f}")
        
        self.best_weights = best_weights
        self.best_score = best_score
        
        return {
            "best_weights": best_weights,
            "best_score": best_score,
            "n_trials": self.config.n_trials,
            "metric": self.config.metric
        }
    
    def validate_weights(self, candidates_path: str, 
                        scorer_functions: Dict) -> Dict:
        """Validate current weights with detailed metrics."""
        from config import SCORER_WEIGHTS
        
        candidates = self.load_candidate_data(candidates_path)
        
        # Evaluate with current weights
        score = self._evaluate_weights(candidates, scorer_functions, SCORER_WEIGHTS)
        
        # Compute detailed metrics
        ndcg_10 = self._compute_ndcg(candidates, k=10)
        ndcg_50 = self._compute_ndcg(candidates, k=50)
        prec_10 = self._compute_precision_at_k(candidates, k=10)
        rank_corr = self._compute_rank_correlation(candidates)
        
        metrics = {
            "overall_score": score,
            "ndcg@10": ndcg_10,
            "ndcg@50": ndcg_50,
            "precision@10": prec_10,
            "rank_correlation": rank_corr,
            "weights": SCORER_WEIGHTS
        }
        
        logger.info("Validation Results:")
        logger.info(f"  NDCG@10: {ndcg_10:.4f}")
        logger.info(f"  NDCG@50: {ndcg_50:.4f}")
        logger.info(f"  Precision@10: {prec_10:.4f}")
        logger.info(f"  Rank Correlation: {rank_corr:.4f}")
        
        return metrics


def run_optimization(candidates_path: str = "data/candidates.jsonl",
                     n_trials: int = 50) -> Dict:
    """
    Convenience function to run weight optimization.
    
    Usage:
        from hyperparameter_tuning import run_optimization
        results = run_optimization("data/candidates.jsonl", n_trials=50)
        print(results["best_weights"])
    """
    from scorers import (
        score_title_role, score_skills, score_career_quality,
        score_experience, score_statement, score_behavioral,
        score_location, score_education
    )
    
    scorer_functions = {
        "title_role": score_title_role,
        "skills": score_skills,
        "career_quality": score_career_quality,
        "experience": score_experience,
        "statement": score_statement,
        "behavioral": score_behavioral,
        "location": score_location,
        "education": score_education,
    }
    
    config = OptimizationConfig(n_trials=n_trials)
    optimizer = WeightOptimizer(config)
    
    results = optimizer.optimize(candidates_path, scorer_functions)
    
    return results


def validate_current_weights(candidates_path: str = "data/candidates.jsonl") -> Dict:
    """Validate the current weights against labeled data."""
    from scorers import (
        score_title_role, score_skills, score_career_quality,
        score_experience, score_statement, score_behavioral,
        score_location, score_education
    )
    
    scorer_functions = {
        "title_role": score_title_role,
        "skills": score_skills,
        "career_quality": score_career_quality,
        "experience": score_experience,
        "statement": score_statement,
        "behavioral": score_behavioral,
        "location": score_location,
        "education": score_education,
    }
    
    optimizer = WeightOptimizer()
    return optimizer.validate_weights(candidates_path, scorer_functions)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    import sys
    if len(sys.argv) > 1:
        candidates_path = sys.argv[1]
    else:
        candidates_path = "data/candidates.jsonl"
    
    # Run validation
    logger.info("Validating current weights...")
    metrics = validate_current_weights(candidates_path)
    
    # Run optimization
    logger.info("\nRunning hyperparameter optimization...")
    results = run_optimization(candidates_path, n_trials=30)
    
    if results:
        logger.info("\n" + "="*60)
        logger.info("OPTIMIZATION COMPLETE")
        logger.info("="*60)
        logger.info(f"Best score: {results['best_score']:.4f}")
        logger.info(f"Best weights:")
        for name, weight in results['best_weights'].items():
            logger.info(f"  {name}: {weight:.4f}")
