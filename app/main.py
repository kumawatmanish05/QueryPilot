import re
from pathlib import Path

from fastapi import HTTPException
from fastapi import FastAPI
from pydantic import BaseModel, Field
from app.services.dataset_manager import get_dataset_engine
from app.services.query_pipeline import run_query


app = FastAPI(
    title="QueryPilot API",
    description="Natural-language-to-SQL analytics assistant",
    version="0.1.0",
)

class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    dataset_id: str = Field(min_length=1, max_length=100)


@app.post("/query")
def query_database(request: QueryRequest):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", request.dataset_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid dataset ID.",
        )

    dataset_path = Path("data/datasets") / f"{request.dataset_id}.db"

    if not dataset_path.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"Dataset '{request.dataset_id}' was not found.",
        )

    database_engine = get_dataset_engine(request.dataset_id)

    try:
        result = run_query(
            question=request.question,
            database_engine=database_engine,
        )
        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    
    finally:
        database_engine.dispose()


@app.get("/")
def home():
    return{
        "message":"Welcome to QueryPilot API",
        "status":"running",
    }

@app.get("/health")
def healtth_check():
    return{
        "status":"healthy",
    }