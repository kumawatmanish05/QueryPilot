from app.services.schema_inspector import get_database_schema

def test_sales_table_exists():
    schema = get_database_schema()

    assert "sales" in schema

def test_sales_column_exists():
    schema = get_database_schema()

    column_names = {
        column["name"]
        for column in schema["sales"]
    }

    excepted_columns ={
        "order_id",
        "order_date",
        "customer_name",
        "product",
        "category",
        "quantity",
        "unit_price",
    }

    assert excepted_columns.issubset(column_names)