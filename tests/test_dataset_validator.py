
from sqlalchemy import create_engine, text

from app.services.dataset_validator import validate_dataset


def test_valid_dataset():
    engine = create_engine("sqlite:///:memory:")

    try:
        with engine.begin() as connection:
            connection.execute(
                text("CREATE TABLE customers (id INTEGER, name TEXT)")
            )

        is_valid, message = validate_dataset(engine)

        assert is_valid is True
        assert message == "Dataset is valid."
    finally:
        engine.dispose()


def test_empty_dataset():
    engine = create_engine("sqlite:///:memory:")

    try:
        is_valid, message = validate_dataset(engine)

        assert is_valid is False
        assert message == "The dataset contains no tables."
    finally:
        engine.dispose()
