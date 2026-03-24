import logging

import psycopg2
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.db import execute_query
from app.query_engine import generate_sql

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AlloyDB AI Query Agent",
    description=(
        "Query a PostgreSQL-compatible AlloyDB database using natural language. "
        "Powered by Google Gemini (Vertex AI) for SQL generation."
    ),
    version="1.0.0",
)


class QueryRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        description="Natural language question to be converted to SQL and executed.",
        examples=["Top DevOps tools"],
    )


class QueryResponse(BaseModel):
    sql: str = Field(..., description="The SQL query generated from the natural language input.")
    results: list[dict] = Field(..., description="Rows returned by the query.")


@app.get("/health", summary="Health check")
def health():
    """Returns service liveness status."""
    return {"status": "ok"}


@app.post(
    "/query",
    response_model=QueryResponse,
    summary="Natural language query",
    description="Accepts a natural language question, converts it to SQL via Gemini, executes it against AlloyDB, and returns the results.",
)
def query(request: QueryRequest):
    """
    Convert a natural language question to SQL and execute it.

    - **query**: Plain-English question about the data.
    """
    try:
        sql = generate_sql(request.query)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Error generating SQL")
        raise HTTPException(status_code=502, detail="Failed to generate SQL from Gemini.") from exc

    try:
        results = execute_query(sql)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except psycopg2.Error as exc:
        logger.exception("Database error while executing query")
        raise HTTPException(status_code=422, detail=f"Database error: {exc.pgerror or str(exc)}") from exc
    except Exception as exc:
        logger.exception("Unexpected error executing query")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.") from exc

    return QueryResponse(sql=sql, results=results)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=False)
