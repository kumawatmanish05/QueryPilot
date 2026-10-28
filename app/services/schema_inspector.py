from sqlalchemy import inspect

from app.core.database import engine

def get_database_schema(database_engine=None) -> dict:
    if database_engine is None:
        database_engine = engine 
    
    inspector  = inspect(database_engine)
    schema = {}

    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)

        schema[table_name] = [
            {
                "name": column["name"],
                "type":str(column["type"]),
                "nullable": column["nullable"],
            }
            for column in columns
        ]

    return schema

if __name__ == "__main__":
    database_schema = get_database_schema()

    for table_name,columns in database_schema.items():
        print(f"\nTable: {table_name}")

        for column in columns:
            print(
                f" {column['name']}:{column['type']}"
                f"(nullable = {column['nullable']})"
            )

from app.services.dataset_manager import get_dataset_engine
from app.services.schema_inspector import get_database_schema
from sqlalchemy import text


def test_schema_inspector_uses_selected_dataset():
    dataset_engine = get_dataset_engine("schema_test")

    try:
        with dataset_engine.begin() as connection:
            connection.execute(
                text("CREATE TABLE customers (id INTEGER, name TEXT)")
            )

        schema = get_database_schema(dataset_engine)

        assert "customers" in schema
        assert "id" in [column["name"] for column in schema["customers"]]
        assert "name" in [column["name"] for column in schema["customers"]]

    finally:
        dataset_engine.dispose()