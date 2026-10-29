
from unittest.mock import patch

import pytest

from app.services.query_pipeline import run_query


def test_unsupported_question_stops_before_sql_validation():
    with (
        patch(
            "app.services.query_pipeline.build_schema_context",
            return_value="Table: uploaded_data",
        ),
        patch(
            "app.services.query_pipeline.generate_sql",
            return_value="CANNOT_ANSWER",
        ),
        patch(
            "app.services.query_pipeline.validate_read_only_sql",
        ) as mock_validate,
        patch(
            "app.services.query_pipeline.execute_read_only_query",
        ) as mock_execute,
    ):
        with pytest.raises(
            ValueError,
            match="cannot be answered using the available dataset",
        ):
            run_query("What is the average employee salary?", database_engine=None)

    mock_validate.assert_not_called()
    mock_execute.assert_not_called()
