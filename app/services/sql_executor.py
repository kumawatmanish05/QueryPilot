from sqlalchemy.exc import OperationalError

from sqlalchemy import create_engine, text , event 
import time 

from app.core.database import engine
from app.services.sql_validator import validate_read_only_sql

DEFAULT_MAX_ROWS = 100
ABSOLUTE_MAX_ROWS = 1000
QUERY_TIMEOUT_SECONDS = 5

class QueryExecutionTimeoutError(TimeoutError):
    """Raised when a SQL query exceeds its execution time budget."""

def execute_read_only_query(
    sql: str,
    max_rows: int = DEFAULT_MAX_ROWS,
) -> list[dict]:
    """Validate and execute SQL through a read-only SQLite connection."""

    if isinstance(max_rows, bool) or not isinstance(max_rows, int):
        raise ValueError("max_rows must be an integer.")

    if not 1 <= max_rows <= ABSOLUTE_MAX_ROWS:
        raise ValueError(
            f"max_rows must be between 1 and {ABSOLUTE_MAX_ROWS}."
        )

    is_valid, message = validate_read_only_sql(sql)
    if not is_valid:
        raise ValueError(message)

    if engine.dialect.name != "sqlite":
        raise RuntimeError(
            "Read-only connection setup currently supports SQLite only."
        )

    database_path = engine.url.database
    if not database_path:
        raise RuntimeError("SQLite database path is not configured.")

    readonly_engine = create_engine(
        f"sqlite:///file:{database_path}?mode=ro&uri=true",
        connect_args={"check_same_thread": False},
    )

    
    try:
        with readonly_engine.connect() as connection:
            raw_connection = connection.connection.driver_connection
            started_at = time.monotonic()

            raw_connection.set_progress_handler(
                lambda: int(
                    time.monotonic() - started_at
                    >= QUERY_TIMEOUT_SECONDS
                ),
                1000,
            )

            limited_sql = f"""
                SELECT *
                FROM ({sql.rstrip().rstrip(';')}) AS querypilot_result
                LIMIT :max_rows
            """

            result = connection.execute(
                text(limited_sql),
                {"max_rows": max_rows},
            )
            rows = result.mappings().all()
            return [dict(row) for row in rows]

    except OperationalError as exc:
        if "interrupted" in str(exc).lower():
            raise QueryExecutionTimeoutError(
                f"Query exceeded the {QUERY_TIMEOUT_SECONDS}-second execution limit."
            ) from exc
        raise

    finally:
        readonly_engine.dispose()



if __name__ == "__main__":
    query = """
    SELECT product, SUM(quantity * unit_price) AS revenue
    FROM sales
    GROUP BY product
    ORDER BY revenue DESC
    """

    for row in execute_read_only_query(query):
        print(row)


