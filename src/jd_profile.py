import re

# Layer 2 Components Weights
WEIGHTS = {
    "title_career": 0.35,
    "skills": 0.30,
    "experience": 0.15,
    "location": 0.10,
    "education": 0.05,
    "github_oss": 0.05
}

# Skill Clusters & Weights
SKILL_CLUSTERS = {
    "embeddings": {
        "weight": 0.28,
        "terms": {"sentence-transformers", "bge", "e5", "openai embeddings", "ada-002", "dense retrieval", "rag", "retrieval augmented generation", "bi-encoder", "semantic search"}
    },
    "vector_db": {
        "weight": 0.25,
        "terms": {"pinecone", "weaviate", "qdrant", "milvus", "faiss", "opensearch", "elasticsearch", "vector store", "hnsw", "approximate nearest neighbor", "hybrid search"}
    },
    "ranking": {
        "weight": 0.22,
        "terms": {"ranking", "ndcg", "mrr", "map", "information retrieval", "bm25", "tf-idf", "learning to rank", "a/b testing", "evaluation framework", "recommendation system", "recommender"}
    },
    "llm_nlp": {
        "weight": 0.15,
        "terms": {"llm", "fine-tuning", "lora", "qlora", "peft", "nlp", "transformers", "bert", "gpt", "language model", "named entity recognition"}
    },
    "python_ml": {
        "weight": 0.10,
        "terms": {"python", "pytorch", "tensorflow", "scikit-learn", "huggingface", "mlflow", "model serving", "fastapi"}
    }
}

PROFICIENCY_SCORE = {
    "beginner": 0.3,
    "intermediate": 0.6,
    "advanced": 0.85,
    "expert": 1.0
}

EDUCATION_TIERS = {
    "tier_1": 1.0,
    "tier_2": 0.80,
    "tier_3": 0.60,
    "tier_4": 0.40,
    "unknown": 0.45
}

# Regex Patterns for Title/Career Component
RE_STRONG_POSITIVE = re.compile(r"\b(ai engineer|artificial intelligence engineer|ml engineer|machine learning engineer|applied scientist|nlp engineer|search engineer|data scientist)\b", re.IGNORECASE)
RE_ADJACENT = re.compile(r"\b(backend|software|data|systems)\s+engineer\b|\bdeveloper\b|\bprogrammer\b", re.IGNORECASE)
RE_HARD_NEGATIVE = re.compile(r"\b(marketing|sales|hr|recruiter|talent|operations|ops|customer support|content writer|mechanical|civil|chemical)\b", re.IGNORECASE)

# Consulting companies for penalty checks
CONSULTING_COMPANIES = {"tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini", "hcl", "tech mahindra"}

# Relevant fields of study
RE_CS_FIELD = re.compile(r"\b(cs|computer science|it|information technology|ml|ai|artificial intelligence|statistics|mathematics|electronics)\b", re.IGNORECASE)

# AI Keywords for career descriptions
RE_AI_KEYWORDS = re.compile(r"\b(embeddings|retrieval|ranking|vector search|rag|llm|fine-tuning|nlp|recommendation|semantic search|pinecone|sentence-transformers)\b", re.IGNORECASE)
