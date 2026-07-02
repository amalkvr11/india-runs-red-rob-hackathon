"""
ml_similarity.py - ML-based semantic similarity scoring using Sentence Transformers.

This module provides:
1. Semantic matching between candidate profiles and job description
2. Skill similarity using embeddings
3. Description relevance scoring
"""

import numpy as np
import logging
from typing import List, Dict, Tuple
import re

logger = logging.getLogger(__name__)

# Job Description for Senior AI Engineer (Series A startup)
JD_TEXT = """
Senior AI Engineer - Series A Startup

We are looking for a Senior AI Engineer to join our fast-growing startup.
The ideal candidate will have:
- 4-8 years of experience in machine learning and AI
- Strong expertise in embeddings, vector search, and retrieval systems
- Experience with vector databases (Pinecone, Weaviate, Qdrant, FAISS, Milvus)
- Proficiency in NLP and Large Language Models (LLMs)
- Knowledge of sentence transformers and semantic search
- Experience with RAG (Retrieval Augmented Generation) systems
- Strong Python skills and ML frameworks (PyTorch, TensorFlow)
- Experience with fine-tuning and deploying models in production
- Familiarity with recommendation and ranking systems
- Experience working in fast-paced startup environments
- Ability to ship production-ready ML systems
- Knowledge of A/B testing and ML evaluation metrics
- Understanding of production deployment (Docker, Kubernetes, AWS/GCP)

Responsibilities:
- Design and implement embeddings and retrieval systems
- Build vector search infrastructure
- Fine-tune and deploy LLMs for production use cases
- Collaborate with product team to ship AI features
- Optimize model performance and latency
- Mentor junior engineers

Keywords: embeddings, vector search, semantic search, LLM, NLP, RAG, 
retrieval augmented generation, Pinecone, Weaviate, sentence transformers,
recommendation systems, ranking, PyTorch, production ML, MLOps
"""


class SemanticSimilarityScorer:
    """
    Semantic similarity scorer using sentence-transformers embeddings.
    Falls back to keyword-based scoring if transformers not available.
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the semantic similarity scorer.
        
        Args:
            model_name: Sentence transformer model to use
        """
        self.model_name = model_name
        self.model = None
        self.jd_embedding = None
        self.skill_embeddings = {}
        self._load_model()
        
    def _load_model(self):
        """Load sentence transformer model with fallback."""
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading sentence transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            
            # Pre-compute JD embedding
            self.jd_embedding = self.model.encode(JD_TEXT, convert_to_tensor=True)
            
            # Pre-compute skill embeddings
            from config import SKILL_GROUPS
            for group_name, max_score, keywords in SKILL_GROUPS:
                skill_text = f"{group_name}: {', '.join(keywords)}"
                self.skill_embeddings[group_name] = self.model.encode(skill_text)
                
            logger.info("Sentence transformer model loaded successfully")
        except ImportError:
            logger.warning("sentence-transformers not installed. Using keyword fallback.")
            self.model = None
        except Exception as e:
            logger.warning(f"Could not load sentence transformer model: {e}. Using keyword fallback.")
            self.model = None
    
    def _get_candidate_text(self, candidate: dict) -> str:
        """Extract comprehensive text representation of candidate."""
        profile = candidate.get("profile", {})
        skills = candidate.get("skills", [])
        career_history = candidate.get("career_history", [])
        
        parts = []
        
        # Title and experience
        title = profile.get("current_title", "")
        yoe = profile.get("years_of_experience", 0)
        if title:
            parts.append(f"Title: {title}")
        if yoe:
            parts.append(f"Experience: {yoe} years")
        
        # Skills
        skill_names = [s.get("name", "") for s in skills if s.get("name")]
        if skill_names:
            parts.append(f"Skills: {', '.join(skill_names[:15])}")
        
        # Career history
        for entry in career_history[:3]:
            title = entry.get("title", "")
            desc = entry.get("description", "")
            if title:
                parts.append(f"Role: {title}")
            if desc:
                # Clean description
                desc_clean = re.sub(r'[^\w\s]', ' ', desc).strip()
                if len(desc_clean) > 20:
                    parts.append(desc_clean[:200])
        
        # Summary/Statement
        summary = profile.get("summary", "")
        statement = profile.get("statement", "")
        if summary:
            parts.append(summary[:300])
        if statement:
            parts.append(statement[:300])
        
        return " | ".join(parts)
    
    def compute_similarity_score(self, candidate: dict) -> Dict:
        """
        Compute semantic similarity score between candidate and JD.
        
        Returns dict with score and detailed breakdown.
        """
        if self.model is None:
            # Fallback to keyword-based scoring
            return self._keyword_fallback(candidate)
        
        try:
            from sentence_transformers import util
            
            # Get candidate text
            candidate_text = self._get_candidate_text(candidate)
            
            if not candidate_text or len(candidate_text) < 20:
                return {
                    "score": 0.0,
                    "reasoning": "insufficient_candidate_text",
                    "method": "semantic",
                    "similarity": 0.0
                }
            
            # Compute embedding
            candidate_embedding = self.model.encode(candidate_text, convert_to_tensor=True)
            
            # Compute cosine similarity
            similarity = util.cos_sim(candidate_embedding, self.jd_embedding).item()
            
            # Normalize to 0-1 range (typical range is -1 to 1, but usually 0.3-0.8 for relevant)
            # Map: < 0.3 -> 0, 0.5 -> 0.5, > 0.7 -> 1.0
            normalized_score = max(0.0, min(1.0, (similarity - 0.3) / 0.4))
            
            # Compute skill-specific similarities
            skill_scores = self._compute_skill_similarities(candidate)
            
            # Combine scores (70% overall similarity, 30% skill match)
            final_score = 0.7 * normalized_score + 0.3 * skill_scores["average"]
            
            return {
                "score": round(final_score, 4),
                "similarity": round(similarity, 4),
                "normalized": round(normalized_score, 4),
                "skill_match": skill_scores,
                "reasoning": f"semantic_sim={similarity:.3f}; skill_match={skill_scores['average']:.3f}; top_skills={skill_scores['top_groups'][:2]}",
                "method": "semantic"
            }
            
        except Exception as e:
            logger.error(f"Error computing semantic similarity: {e}")
            return self._keyword_fallback(candidate)
    
    def _compute_skill_similarities(self, candidate: dict) -> Dict:
        """Compute skill-specific semantic matches."""
        from sentence_transformers import util
        from config import SKILL_GROUPS
        
        skills = candidate.get("skills", [])
        skill_names = [s.get("name", "").lower() for s in skills if s.get("name")]
        
        if not skill_names or not self.skill_embeddings:
            return {"average": 0.0, "max": 0.0, "top_groups": []}
        
        # Encode candidate skills
        candidate_skills_text = ", ".join(skill_names[:20])
        candidate_skills_emb = self.model.encode(candidate_skills_text)
        
        group_scores = []
        for group_name, max_score, keywords in SKILL_GROUPS:
            if group_name in self.skill_embeddings:
                similarity = util.cos_sim(
                    candidate_skills_emb, 
                    self.skill_embeddings[group_name]
                ).item()
                group_scores.append((group_name, similarity, max_score))
        
        # Sort by similarity
        group_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Get top matches
        top_groups = [f"{name}({sim:.2f})" for name, sim, _ in group_scores[:3]]
        
        # Weight by group importance
        weighted_sum = sum(sim * max_score for _, sim, max_score in group_scores)
        total_weight = sum(max_score for _, _, max_score in group_scores)
        
        avg_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        max_score = max([sim for _, sim, _ in group_scores]) if group_scores else 0.0
        
        return {
            "average": round(avg_score, 4),
            "max": round(max_score, 4),
            "top_groups": top_groups,
            "all_scores": {name: round(sim, 3) for name, sim, _ in group_scores}
        }
    
    def _keyword_fallback(self, candidate: dict) -> Dict:
        """Fallback keyword-based scoring when transformers not available."""
        from config import SKILL_GROUPS, ML_DESCRIPTION_KEYWORDS
        
        profile = candidate.get("profile", {})
        skills = candidate.get("skills", [])
        career_history = candidate.get("career_history", [])
        
        # Extract text
        summary = (profile.get("summary") or "").lower()
        statement = (profile.get("statement") or "").lower()
        title = (profile.get("current_title") or "").lower()
        
        all_text = f"{title} {summary} {statement}"
        
        for entry in career_history:
            all_text += f" {(entry.get('description') or '').lower()}"
        
        # Count JD keyword matches
        jd_keywords = [
            "embeddings", "vector search", "semantic search", "llm", "rag",
            "retrieval augmented", "pinecone", "weaviate", "sentence transformers",
            "recommendation", "ranking", "pytorch", "production ml", "mlops",
            "fine-tuning", "nlp", "ai", "machine learning"
        ]
        
        matches = sum(1 for kw in jd_keywords if kw in all_text)
        keyword_score = min(matches / 10, 1.0) * 0.6  # Cap at 60%
        
        # Skill group matching
        skill_names = [s.get("name", "").lower() for s in skills]
        skill_text = " ".join(skill_names)
        
        group_matches = 0
        total_groups = 0
        for group_name, max_score, keywords in SKILL_GROUPS:
            total_groups += 1
            if any(kw.lower() in skill_text for kw in keywords):
                group_matches += 1
        
        skill_score = (group_matches / total_groups) if total_groups > 0 else 0.0
        
        # Combine
        final_score = 0.4 * keyword_score + 0.6 * skill_score
        
        return {
            "score": round(final_score, 4),
            "reasoning": f"keyword_fallback; matches={matches}; groups={group_matches}/{total_groups}",
            "method": "keyword_fallback",
            "similarity": None
        }


# Global scorer instance (singleton)
_semantic_scorer = None

def get_semantic_scorer() -> SemanticSimilarityScorer:
    """Get or create the global semantic similarity scorer."""
    global _semantic_scorer
    if _semantic_scorer is None:
        _semantic_scorer = SemanticSimilarityScorer()
    return _semantic_scorer


def score_ml_similarity(candidate: dict) -> Dict:
    """
    Wrapper function to compute ML-based similarity score.
    
    This can be added as an additional scorer dimension or used to 
    enhance existing scores.
    
    Returns dict with:
        - score: float (0-1)
        - reasoning: str
        - similarity: float (raw cosine similarity)
        - method: str (semantic or keyword_fallback)
    """
    scorer = get_semantic_scorer()
    return scorer.compute_similarity_score(candidate)


def batch_compute_similarity(candidates: List[dict], batch_size: int = 100) -> List[Dict]:
    """
    Efficiently compute similarity for multiple candidates.
    
    Args:
        candidates: List of candidate dictionaries
        batch_size: Batch size for processing
        
    Returns:
        List of result dictionaries
    """
    scorer = get_semantic_scorer()
    results = []
    
    for i in range(0, len(candidates), batch_size):
        batch = candidates[i:i+batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}: {len(batch)} candidates")
        
        for candidate in batch:
            result = scorer.compute_similarity_score(candidate)
            results.append(result)
    
    return results


if __name__ == "__main__":
    # Test the scorer
    logging.basicConfig(level=logging.INFO)
    
    test_candidate = {
        "candidate_id": "TEST_001",
        "profile": {
            "current_title": "Senior ML Engineer",
            "years_of_experience": 6,
            "summary": "Expert in embeddings and vector search with 5 years of experience building RAG systems.",
            "statement": "Passionate about NLP and LLMs. Led team building semantic search at scale."
        },
        "skills": [
            {"name": "Pinecone", "proficiency": "expert"},
            {"name": "Sentence Transformers", "proficiency": "expert"},
            {"name": "Python", "proficiency": "expert"},
            {"name": "PyTorch", "proficiency": "advanced"},
            {"name": "LangChain", "proficiency": "advanced"}
        ],
        "career_history": [
            {
                "title": "Senior ML Engineer",
                "description": "Built vector search infrastructure with Pinecone and FAISS. Fine-tuned embeddings for domain-specific retrieval.",
                "duration_months": 24
            }
        ]
    }
    
    result = score_ml_similarity(test_candidate)
    print("\nTest Result:")
    print(f"Score: {result['score']}")
    print(f"Method: {result['method']}")
    print(f"Reasoning: {result['reasoning']}")
    if 'similarity' in result:
        print(f"Raw Similarity: {result['similarity']}")
