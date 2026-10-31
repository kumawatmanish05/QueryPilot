import re
from pathlib import Path
import logging
import uuid 
import pandas as pd
import csv
import io
from sqlalchemy import create_engine , text 
import json 

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

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5501",
        "http://localhost:5501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    dataset_id: str = Field(min_length=1, max_length=100)



@app.post("/query")
def query_database(request: QueryRequest):

    # Validate dataset ID
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
        # Validate uploaded dataset
        is_valid, message = validate_dataset(database_engine)

        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=message,
            )

        # Generate SQL and execute query
        result = run_query(
            question=request.question,
            database_engine=database_engine,
        )

        # Save query history separately.
        # History failure must not prevent query results from being returned.
        try:
            with database_engine.begin() as connection:
                connection.execute(
                    text("""
                        INSERT INTO query_history (
                            question,
                            generated_sql,
                            results_json,
                            row_count
                        )
                        VALUES (
                            :question,
                            :generated_sql,
                            :results_json,
                            :row_count
                        )
                    """),
                    {
                        "question": request.question,
                        "generated_sql": result["sql"],
                        "results_json": json.dumps(result["rows"]),
                        "row_count": result["row_count"],
                    },
                )

        except Exception:
            logger.exception("Failed to save query history")

        # Return query results
        return result

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        logger.exception(
            "Unexpected error while processing QueryPilot query"
        )

        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your query.",
        ) from None

    finally:
        database_engine.dispose()


MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB



@app.post("/datasets/upload", status_code=201)
async def upload_dataset(file: UploadFile = File(...)):

    # Validate file extension
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file.",
        )

    # Read uploaded file
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

    # Validate dataset
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

    # Generate unique dataset ID
    dataset_id = uuid.uuid4().hex

    dataset_path = Path("data/datasets") / f"{dataset_id}.db"
    dataset_path.parent.mkdir(parents=True, exist_ok=True)

    database_engine = create_engine(
        f"sqlite:///{dataset_path.resolve().as_posix()}"
    )

    try:
        with database_engine.begin() as connection:

            # Store uploaded CSV data
            df.to_sql(
                name="uploaded_data",
                con=connection,
                if_exists="fail",
                index=False,
            )

            # Create query history table
            connection.exec_driver_sql("""
                CREATE TABLE query_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    generated_sql TEXT NOT NULL,
                    results_json TEXT NOT NULL,
                    row_count INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

    except Exception:
        logger.exception("Failed to store uploaded dataset")

        # Close database connection before deleting file
        database_engine.dispose()

        dataset_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail="Could not store the uploaded dataset.",
        ) from None

    finally:
        database_engine.dispose()

    # IMPORTANT: Return successful upload response
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