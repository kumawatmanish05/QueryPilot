from app.services.sql_validator import validate_read_only_sql

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