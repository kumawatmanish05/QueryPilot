from app.services.dataset_manager import get_dataset_engine
from app.services.query_pipeline import run_query
from app.services.schema_context import build_schema_context
from app.services.data_loader import load_csv_to_table

database_engine = get_dataset_engine("sales_demo")

load_csv_to_table(
    csv_path="data/sample_sales.csv",
    table_name="sales",
    database_engine=database_engine,
)

try:
    print("DATABASE SCHEMA:")
    print(build_schema_context(database_engine))
    result = run_query(
        question="What is the total revenue for each product?",
        database_engine=database_engine,
    )

    print("Question:", result["question"])
    print("Generated SQL:", result["sql"])
    print("Row count:", result["row_count"])
    print("Results:", result["rows"])

finally:
    database_engine.dispose()