import pytest
from sqlalchemy import text
from pathlib import Path

from app.services.dataset_manager import get_dataset_database_path
from app.services.dataset_manager import get_dataset_engine
from app.services.data_loader import load_csv_to_table

def test_valid_dataset_id():
    path = get_dataset_database_path("sales_demo")
    assert path.name == "sales_demo.db"


def test_invalid_dataset_id():
    with pytest.raises(ValueError):
        get_dataset_database_path("../../other_file")

def test_datasets_use_separate_databases():
    datasets_dir = Path("data/datasets")
    datasets_dir.mkdir(parents=True, exist_ok=True)

    for dataset_id in ("test_sales", "test_customers"):
        database_path = datasets_dir / f"{dataset_id}.db"
        if database_path.exists():
            database_path.unlink()

    sales_engine = get_dataset_engine("test_sales")
    customers_engine = get_dataset_engine("test_customers")

    try:
        with sales_engine.begin() as connection:
            connection.execute(
                text("CREATE TABLE sales (id INTEGER)")
            )

        with customers_engine.connect() as connection:
            result = connection.execute(
                text(
                    "SELECT name FROM sqlite_master "
                    "WHERE type = 'table' AND name = 'sales'"
                )
            ).fetchall()

        assert result == []

    finally:
        sales_engine.dispose()
        customers_engine.dispose()


def test_csv_loads_into_selected_dataset():
    dataset_engine = get_dataset_engine("loader_test")

    try:
        rows_loaded = load_csv_to_table(
            csv_path="data/sample_sales.csv",
            table_name="sales",
            database_engine=dataset_engine,
        )

        assert rows_loaded == 10

        with dataset_engine.connect() as connection:
            count = connection.execute(
                text("SELECT COUNT(*) FROM sales")
            ).scalar_one()

        assert count == 10

    finally:
        dataset_engine.dispose()