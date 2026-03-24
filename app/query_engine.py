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
if GCP_PROJECT:
    vertexai.init(project=GCP_PROJECT, location=GCP_LOCATION)

_model = GenerativeModel(
    model_name=GEMINI_MODEL,
    system_instruction=SYSTEM_PROMPT,
)


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
    response = _model.generate_content(natural_language_query)
    sql = _extract_sql(response.text)

    logger.info("Generated SQL: %s", sql)

    if not sql.strip().upper().startswith("SELECT"):
        raise ValueError(
            f"Model returned a non-SELECT statement, which is not allowed: {sql}"
        )

    return sql
