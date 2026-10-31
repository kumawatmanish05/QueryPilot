import re
from pathlib import Path

from sqlalchemy import create_engine

DATASETS_DIR = Path("data/datasets")


def get_dataset_database_path(dataset_id: str) -> Path:
    """Return the database path for a dataset."""
    if not re.fullmatch(r"[A-Za-z0-9_-]+", dataset_id):
        raise ValueError("Invalid dataset ID.")

    return DATASETS_DIR / f"{dataset_id}.db"


def get_dataset_engine(dataset_id: str):
    """Create a SQLAlchemy engine for a dataset database."""
    database_path = get_dataset_database_path(dataset_id)
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)

    return create_engine(
        f"sqlite:///{database_path.as_posix()}",
        connect_args={"check_same_thread": False},
    )