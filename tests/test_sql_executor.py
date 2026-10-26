
import pytest
import app.services.sql_executor as sql_executor
from app.services.sql_executor import execute_read_only_query
from app.services.sql_executor import (QueryExecutionTimeoutError ,execute_read_only_query, )


def test_default_result_limit():
    rows = execute_read_only_query("SELECT * FROM sales")

    assert len(rows) <= 100


def test_custom_result_limit():
    rows = execute_read_only_query(
        "SELECT * FROM sales",
        max_rows=3,
    )

    assert len(rows) == 3


def test_result_limit_cannot_exceed_maximum():
    with pytest.raises(ValueError):
        execute_read_only_query(
            "SELECT * FROM sales",
            max_rows=1001,
        )



def test_expensive_query_is_interrupted_by_timeout(monkeypatch):
    monkeypatch.setattr(sql_executor, "QUERY_TIMEOUT_SECONDS", 0.001)

    query = """
    WITH RECURSIVE numbers(x) AS (
        SELECT 1
        UNION ALL
        SELECT x + 1 FROM numbers WHERE x < 1000000
    )
    SELECT SUM(a.x * b.x)
    FROM numbers AS a
    CROSS JOIN numbers AS b
    """

    with pytest.raises(QueryExecutionTimeoutError):
        sql_executor.execute_read_only_query(query)

    
