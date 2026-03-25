import os
import logging
import re

import vertexai
from vertexai.generative_models import GenerativeModel
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GCP_PROJECT = os.getenv("GCP_PROJECT", "")
GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
USE_GEMINI = os.getenv("USE_GEMINI", "true").lower() == "true"

# Schema description injected into the prompt so Gemini knows the table structure.
DB_SCHEMA = """
Tables available:

ai_tools (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    popularity_score INT
);

Sample categories: LLM Framework, Backend, Vector DB, LLM API, ML Platform, DevOps
"""

SYSTEM_PROMPT = (
    "You are a PostgreSQL expert. Given the following database schema and a user's "
    "natural language question, generate a single valid PostgreSQL SELECT query that "
    "answers the question. Return ONLY the raw SQL query — no markdown, no explanation, "
    "no code fences.\n\nSchema:\n" + DB_SCHEMA
)

# Initialize Vertex AI and build the model once at module load time.
_model = None
if USE_GEMINI:
    if GCP_PROJECT:
        vertexai.init(project=GCP_PROJECT, location=GCP_LOCATION)

    _model = GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=SYSTEM_PROMPT,
    )


def _escape_like(value: str) -> str:
    return value.replace("'", "''")


def _fallback_sql(natural_language_query: str) -> str:
    """Best-effort local SQL generator used when Gemini is unavailable."""
    q = natural_language_query.lower().strip()
    escaped = _escape_like(natural_language_query.strip())

    category_map = {
        "backend": "Backend",
        "vector": "Vector DB",
        "vector db": "Vector DB",
        "devops": "DevOps",
        "llm api": "LLM API",
        "api": "LLM API",
        "framework": "LLM Framework",
        "ml": "ML Platform",
    }

    category = None
    for key, value in category_map.items():
        if key in q:
            category = value
            break

    top_intent = any(token in q for token in ["top", "best", "most popular", "popular"])

    if category and top_intent:
        return (
            "SELECT id, name, category, description, popularity_score "
            f"FROM ai_tools WHERE category ILIKE '%{_escape_like(category)}%' "
            "ORDER BY popularity_score DESC LIMIT 10;"
        )

    if category:
        return (
            "SELECT id, name, category, description, popularity_score "
            f"FROM ai_tools WHERE category ILIKE '%{_escape_like(category)}%' "
            "ORDER BY popularity_score DESC;"
        )

    if top_intent:
        return (
            "SELECT id, name, category, description, popularity_score "
            "FROM ai_tools ORDER BY popularity_score DESC LIMIT 10;"
        )

    if escaped:
        return (
            "SELECT id, name, category, description, popularity_score "
            "FROM ai_tools "
            f"WHERE name ILIKE '%{escaped}%' OR category ILIKE '%{escaped}%' OR description ILIKE '%{escaped}%' "
            "ORDER BY popularity_score DESC LIMIT 20;"
        )

    return "SELECT id, name, category, description, popularity_score FROM ai_tools ORDER BY popularity_score DESC LIMIT 20;"


def _extract_sql(text: str) -> str:
    """Strip markdown code fences if the model includes them despite instructions."""
    # Remove ```sql ... ``` or ``` ... ``` blocks
    text = re.sub(r"```(?:sql)?\s*", "", text, flags=re.IGNORECASE)
    text = text.replace("```", "")
    return text.strip()


def generate_sql(natural_language_query: str) -> str:
    """
    Convert a natural language query into a PostgreSQL SELECT statement.

    Args:
        natural_language_query: The user's question in plain English.

    Returns:
        A SQL SELECT query string.

    Raises:
        ValueError: If the generated query is not a SELECT statement.
        Exception: On Vertex AI / Gemini errors.
    """
    if not USE_GEMINI:
        sql = _fallback_sql(natural_language_query)
        logger.info("Gemini disabled by USE_GEMINI=false. Using fallback SQL: %s", sql)
        return sql

    try:
        response = _model.generate_content(natural_language_query)
        sql = _extract_sql(response.text)

        logger.info("Generated SQL via Gemini: %s", sql)

        if not sql.strip().upper().startswith("SELECT"):
            raise ValueError(
                f"Model returned a non-SELECT statement, which is not allowed: {sql}"
            )

        return sql
    except Exception:
        sql = _fallback_sql(natural_language_query)
        logger.exception("Gemini SQL generation failed. Using fallback SQL: %s", sql)
        return sql
