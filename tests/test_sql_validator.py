from app.services.sql_validator import validate_read_only_sql
from unittest.mock import patch
from app.services import sql_executor

def test_valid_select_query_is_allowed():
    is_valid, _ = validate_read_only_sql("SELECT * FROM sales")
    assert is_valid is True

def test_drop_query_is_rejected():
    is_valid, _ = validate_read_only_sql("DROP TABLE sales")
    assert is_valid is False

def test_delete_query_is_rejected():
    is_valid, _ = validate_read_only_sql("DELETE FROM sales")
    assert is_valid is False

def test_empty_query_is_rejected():
    is_valid, _ = validate_read_only_sql("")
    assert is_valid is False

def test_multiple_statements_are_rejected():
    sql = "SELECT * FROM sales; DROP TABLE sales"
    is_valid, _ = validate_read_only_sql(sql)
    assert is_valid is False


def test_keyword_inside_string_is_allowed():
    sql = "SELECT * FROM sales WHERE product = 'DROP'"
    is_valid, _ = validate_read_only_sql(sql)
    assert is_valid is True


def test_nested_select_query_is_allowed():
    sql = """
    SELECT product
    FROM sales
    WHERE unit_price > (
        SELECT AVG(unit_price)
        FROM sales
    )
    """
    is_valid, _ = validate_read_only_sql(sql)
    assert is_valid is True


def test_rejected_query_never_reaches_database():
    with patch.object(sql_executor, "engine") as mock_engine:
        try:
            sql_executor.execute_read_only_query("DROP TABLE sales")
            assert False, "Expected ValueError for rejected SQL"
        except ValueError:
            pass

        mock_engine.connect.assert_not_called()

