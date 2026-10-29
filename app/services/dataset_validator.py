
from sqlalchemy.engine import Engine

from app.services.schema_inspector import get_database_schema


def validate_dataset(database_engine: Engine) -> tuple[bool, str]:
    """Check whether a dataset contains at least one usable table."""

    try:
        schema = get_database_schema(database_engine)
    except Exception:
        return False, "Could not inspect the dataset schema."

    if not schema:
        return False, "The dataset contains no tables."

    usable_tables = {
        table_name: columns
        for table_name, columns in schema.items()
        if columns
    }

    if not usable_tables:
        return False, "The dataset contains no usable tables."

    return True, "Dataset is valid."
