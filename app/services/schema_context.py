from app.services.schema_inspector import get_database_schema

def build_schema_context(database_engine=None) -> str:
    """Convert database Schema metadata into text for an LLM prompt. """

    schema = get_database_schema(database_engine)

    if not schema :
        return "No tables are available in this database."

    schema_lines = []

    for table_name , columns in schema.items():
        schema_lines.append(f"Table:{table_name}")

        for column in columns:
            column_name = column["name"]
            column_type = column["type"]
            nullable = column["nullable"]

            schema_lines.append(
                f"  - {column_name} ({column_type} , nullable={nullable})"
            )

    return "\n".join(schema_lines)

if __name__ == "__main__":
    print(build_schema_context())