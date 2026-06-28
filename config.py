"""
config.py — Central configuration for the Redrob Hackathon ranker.

All JD-derived constants, scoring weights, skill taxonomies, and
tunable thresholds live here so they can be adjusted in one place.
"""

from datetime import date

# ============================================================================
# Reference date for recency calculations
# ============================================================================
REFERENCE_DATE = date(2026, 6, 1)  # approximate "now" for the dataset

# ============================================================================
# Composite scorer weights  (must sum to 1.0)
# ============================================================================
SCORER_WEIGHTS = {
    "title_role":        0.20,
    "skills":            0.22,
    "career_quality":    0.20,
    "experience":        0.15,
    "statement":         0.08,
    "behavioral":        0.06,
    "location":          0.04,
    "education":         0.05,
}

# ============================================================================
# Title / role tier mapping
# Normalized lowercase → relevance score 0.0–1.0
# ============================================================================
TITLE_TIERS = {
    # --- Tier 1.0: Direct AI/ML engineering roles ---
    "ai engineer":                          1.0,
    "senior ai engineer":                   1.0,
    "ml engineer":                          1.0,
    "machine learning engineer":            1.0,
    "senior machine learning engineer":     1.0,
    "junior ml engineer":                   0.85,
    "nlp engineer":                         1.0,
    "data scientist":                       0.9,
    "senior data scientist":                0.95,
    "search engineer":                      0.95,
    "ranking engineer":                     1.0,
    "recommendation engineer":              0.95,
    "applied scientist":                    0.9,
    "research engineer":                    0.8,

    # --- Tier 0.7: Adjacent technical roles ---
    "data engineer":                        0.7,
    "senior data engineer":                 0.75,
    "backend engineer":                     0.6,
    "senior backend engineer":              0.65,
    "software engineer":                    0.5,
    "senior software engineer":             0.55,
    "full stack developer":                 0.4,
    "full-stack developer":                 0.4,
    "fullstack developer":                  0.4,
    "devops engineer":                      0.3,
    "platform engineer":                    0.35,

    # --- Tier 0.1–0.2: Weakly adjacent ---
    "project manager":                      0.15,
    "product manager":                      0.2,
    "business analyst":                     0.1,
    "content writer":                       0.05,

    # --- Tier 0.0: Non-technical / irrelevant ---
    "marketing manager":                    0.0,
    "hr manager":                           0.0,
    "accountant":                           0.0,
    "customer support":                     0.0,
    "sales executive":                      0.0,
    "civil engineer":                       0.0,
    "mechanical engineer":                  0.0,
    "graphic designer":                     0.05,
    "operations manager":                   0.0,
}

# Keywords in career descriptions that suggest actual AI/ML work
# (used to rescue candidates whose titles are misleading)
ML_DESCRIPTION_KEYWORDS = [
    "machine learning", "deep learning", "neural network", "embedding",
    "retrieval", "ranking", "recommendation", "nlp", "natural language",
    "transformer", "bert", "gpt", "llm", "fine-tun", "fine tun",
    "vector search", "vector database", "faiss", "pinecone", "weaviate",
    "qdrant", "milvus", "elasticsearch", "opensearch",
    "model training", "model deployment", "model serving",
    "pytorch", "tensorflow", "scikit-learn", "xgboost",
    "feature engineering", "data pipeline", "ml pipeline",
    "a/b test", "ndcg", "mrr", "precision", "recall",
    "rag", "retrieval augmented", "sentence-transformer",
    "hugging face", "huggingface",
]

# Keywords that indicate production/shipping experience
PRODUCTION_KEYWORDS = [
    "production", "deployed", "shipped", "launched", "scaled",
    "real users", "real-time", "real time", "end-to-end",
    "api", "microservice", "docker", "kubernetes", "aws", "gcp", "azure",
    "ci/cd", "monitoring", "observability", "latency",
]

# ============================================================================
# Skills taxonomy — grouped by relevance to the JD
# Each group: (group_name, max_group_score, list_of_skill_keywords)
# ============================================================================
SKILL_GROUPS = [
    (
        "embeddings_retrieval", 1.0,
        [
            "embeddings", "embedding", "sentence-transformers", "sentence transformers",
            "bge", "e5", "retrieval", "rag", "retrieval augmented",
            "information retrieval", "dense retrieval", "hybrid search",
            "semantic search", "word2vec", "doc2vec",
        ]
    ),
    (
        "vector_db", 1.0,
        [
            "pinecone", "weaviate", "qdrant", "milvus", "faiss",
            "elasticsearch", "opensearch", "vector search", "vector database",
            "annoy", "chroma", "chromadb",
        ]
    ),
    (
        "python", 0.8,
        ["python"]
    ),
    (
        "nlp_llm", 0.9,
        [
            "nlp", "natural language processing", "transformers", "bert", "gpt",
            "llm", "large language model", "fine-tuning llms", "fine-tuning",
            "lora", "qlora", "peft", "hugging face", "huggingface",
            "langchain", "llamaindex", "text generation", "text classification",
            "named entity recognition", "ner", "sentiment analysis",
            "question answering", "summarization", "tokenization",
        ]
    ),
    (
        "ml_eval", 0.7,
        [
            "ndcg", "mrr", "map", "precision", "recall", "f1",
            "a/b testing", "ab testing", "evaluation", "mlflow",
            "experiment tracking", "model evaluation", "ranking metrics",
            "learning to rank", "learning-to-rank",
        ]
    ),
    (
        "ml_frameworks", 0.6,
        [
            "pytorch", "tensorflow", "scikit-learn", "sklearn",
            "xgboost", "lightgbm", "catboost", "keras",
            "jax", "spacy", "nltk", "gensim", "opencv",
        ]
    ),
    (
        "data_infra", 0.4,
        [
            "spark", "pyspark", "airflow", "kafka", "sql",
            "docker", "kubernetes", "k8s", "aws", "gcp", "azure",
            "snowflake", "databricks", "dbt", "bigquery",
            "redis", "mongodb", "postgresql", "mysql",
        ]
    ),
]

# Proficiency weights
PROFICIENCY_WEIGHTS = {
    "expert":       1.0,
    "advanced":     0.8,
    "intermediate": 0.5,
    "beginner":     0.3,
}

# ============================================================================
# Consulting / services companies (explicit JD disqualifiers)
# ============================================================================
CONSULTING_FIRMS = {
    "tcs", "tata consultancy", "tata consultancy services",
    "infosys",
    "wipro",
    "accenture",
    "cognizant", "cognizant technology solutions",
    "capgemini",
    "hcl", "hcl technologies",
    "tech mahindra",
    "mindtree",  # Now part of LTIMindtree
    "ltimindtree", "lti",
    "mphasis",
    "hexaware",
    "persistent systems",
    "zensar",
    "l&t infotech",
    "cyient",
    "niit technologies",
    "birlasoft",
    "coforge",
}

# ============================================================================
# Location scoring
# ============================================================================
INDIA_PREFERRED_CITIES = {
    "pune", "noida", "delhi", "new delhi", "delhi ncr", "ncr",
    "gurgaon", "gurugram", "hyderabad", "mumbai", "bangalore",
    "bengaluru", "chennai", "kolkata",
}

INDIA_KEYWORDS = {"india"}

# ============================================================================
# Education scoring
# ============================================================================
CS_RELATED_FIELDS = {
    "computer science", "computer engineering", "software engineering",
    "information technology", "artificial intelligence", "machine learning",
    "data science", "statistics", "mathematics", "applied mathematics",
    "computational", "electronics and communication", "ece",
    "electrical engineering", "electronics",
}

TIER_SCORES = {
    "tier_1": 0.20,
    "tier_2": 0.10,
    "tier_3": 0.00,
    "tier_4": -0.05,
    "unknown": 0.00,
}

DEGREE_LEVEL_SCORES = {
    "ph.d": 0.10,
    "phd": 0.10,
    "m.tech": 0.08,
    "mtech": 0.08,
    "m.e.": 0.06,
    "m.s.": 0.06,
    "m.sc": 0.05,
    "msc": 0.05,
    "b.tech": 0.02,
    "btech": 0.02,
    "b.e.": 0.02,
    "b.sc": 0.00,
    "bsc": 0.00,
}

# ============================================================================
# Behavioral signal weights (within the behavioral sub-scorer)
# ============================================================================
BEHAVIORAL_WEIGHTS = {
    "recency":                0.18,
    "open_to_work":           0.15,
    "response_rate":          0.15,
    "response_time":          0.08,
    "notice_period":          0.12,
    "interview_completion":   0.10,
    "verification":           0.07,
    "github":                 0.05,
    "platform_engagement":    0.05,
    "salary_alignment":       0.05,
}

# JD salary range (inferred from "Series A" + "Senior AI Engineer" in India)
JD_SALARY_RANGE_LPA = {"min": 20, "max": 60}

# ============================================================================
# Honeypot detection thresholds
# ============================================================================
HONEYPOT_THRESHOLDS = {
    # If a candidate claims "expert" in N+ skills with avg endorsements < X
    "expert_skill_count_threshold": 5,
    "expert_low_endorsement_avg": 5,
    # If yoe is more than X months above career history total
    "yoe_career_gap_months": 36,
    # If assessment score is below X for a self-declared expert/advanced skill
    "assessment_contradiction_threshold": 30,
    # Max reasonable expert skills for any candidate
    "max_reasonable_expert_skills": 6,
    # Skill duration: expert with < N months
    "expert_min_duration_months": 12,
}

# ============================================================================
# Statement / summary scoring
# ============================================================================
STATEMENT_ML_KEYWORDS = [
    "machine learning", "deep learning", "neural network", "nlp", "llm",
    "artificial intelligence", "data science", "computer vision",
    "recommendation system", "search engine", "ranking algorithm",
    "information retrieval", "ai engineer", "ml engineer",
    "data scientist", "applied scientist", "research scientist",
    "natural language processing", "computer vision engineer",
    "ai researcher", "ml researcher", "generative ai", "genai",
    "large language model", "transformer", "embedding", "vector search",
    "rag", "retrieval augmented generation", "recommender system",
    "predictive model", "statistical model", "a/b testing",
    "experimentation", "causal inference",
]

STATEMENT_STARTUP_KEYWORDS = [
    "startup", "early-stage", "series a", "series b", "fast-paced",
    "building from scratch", "0 to 1", "zero to one",
]

STATEMENT_IMPACT_KEYWORDS = [
    "led", "lead", "managed", "architected", "designed", "built",
    "developed", "scaled", "optimized", "improved", "delivered",
    "launched", "shipped", "mentored", "hired", "founded",
]

# ============================================================================
# Better reasoning config
# ============================================================================
# How many specific facts to include in reasoning (for variation)
REASONING_MIN_FACTS = 2
REASONING_MAX_FACTS = 4

# ============================================================================
# Additional honeypot detection thresholds
# ============================================================================
HONEYPOT_FUTURE_ACTIVITY_DAYS = 30  # If last_active_date is > N days after REFERENCE_DATE
HONEYPOT_MAX_YOE = 50               # Maximum believable years of experience
HONEYPOT_MIN_PROFILE_COMPLETENESS = 15
HONEYPOT_SKILL_COUNT_UNREALISTIC = 30  # More than this many skills is suspicious
HONEYPOT_ASSESSMENT_MIN_SCORE = 10     # Minimum possible assessment score
HONEYPOT_MAX_REASONABLE_CAREERS = 15   # More than this many career entries is suspicious

# ============================================================================
# Output configuration
# ============================================================================
TOP_K = 100  # Number of candidates to output
