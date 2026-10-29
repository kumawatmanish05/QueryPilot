from sqlalchemy.engine import Engine

from app.services.schema_context import build_schema_context
from app.services.llm_client import generate_sql
from app.services.sql_validator import validate_read_only_sql
from app.services.sql_executor import execute_read_only_query

def run_query(question:str, database_engine: Engine) -> dict:
    """Convert a natural-language question into safe SQL results."""

    schema_context = build_schema_context(database_engine)

    sql = generate_sql(
        question=question,
        schema_context=schema_context,
    )

    print("RAW GENERATED SQL:", repr(sql))

    is_valid, message = validate_read_only_sql(sql)

    print("VALIDATION RESULT:", is_valid)
    print("VALIDATION MESSAGE:", message)

    if not is_valid:
        raise ValueError(f"Generated SQL was rejected: {message}")

    rows = execute_read_only_query(
        sql = sql,
        database_engine=database_engine,
    )

    return{
        "question": question,
        "sql": sql,
        "rows":rows,
        "row_count": len(rows),
    }