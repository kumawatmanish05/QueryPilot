import re
from pathlib import Path
import logging
import uuid 
import pandas as pd
import csv
import io
from sqlalchemy import create_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from fastapi import HTTPException
from fastapi import FastAPI , UploadFile , File 
from pydantic import BaseModel, Field
from app.services.dataset_manager import get_dataset_engine
from app.services.query_pipeline import run_query
from app.services.dataset_validator import validate_dataset


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
        is_valid, message = validate_dataset(database_engine)

        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=message,
            )
        
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

    except Exception:
        logger.exception("Unexpected error while processing QueryPilot Result")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your query.",
        ) from None
    
    finally:
        database_engine.dispose()


MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB


@app.post("/datasets/upload", status_code=201)
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file.",
        )

    content = await file.read(MAX_UPLOAD_BYTES + 1)

    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail="File is too large. Maximum size is 5 MB.",
        )

    try:
        df = pd.read_csv(io.BytesIO(content))
    except (pd.errors.ParserError, UnicodeDecodeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid CSV.",
        ) from None
    finally:
        await file.close()

    if df.empty:
        raise HTTPException(
            status_code=400,
            detail="The uploaded CSV contains no data rows.",
        )

    if len(df.columns) == 0 or not df.columns.is_unique:
        raise HTTPException(
            status_code=400,
            detail="The CSV must have unique column names.",
        )

    dataset_id = uuid.uuid4().hex
    dataset_path = Path("data/datasets") / f"{dataset_id}.db"
    dataset_path.parent.mkdir(parents=True, exist_ok=True)

    database_engine = create_engine(
        f"sqlite:///{dataset_path.resolve().as_posix()}"
    )

    try:
        with database_engine.begin() as connection:
            df.to_sql(
                name="uploaded_data",
                con=connection,
                if_exists="fail",
                index=False,
            )
    except Exception:
        dataset_path.unlink(missing_ok=True)
        logger.exception("Failed to store uploaded dataset")
        raise HTTPException(
            status_code=500,
            detail="Could not store the uploaded dataset.",
        ) from None
    finally:
        database_engine.dispose()

    return {
        "dataset_id": dataset_id,
        "rows_loaded": len(df),
        "columns": df.columns.tolist(),
        "message": "Dataset uploaded successfully.",
    }


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