from sqlalchemy import inspect

from app.core.database import engine

def get_database_schema() -> dict:
    inspector  = inspect(engine)
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