from app.services.prompt_builder import build_sql_prompt

def test_prompt_includes_question_and_schema():
    prompt = build_sql_prompt(
        question="What is the total revenue for each product?",
        schema_context = "Table: sales\n - product (TEXT)\n - quantity (BIGINT)\n - unit_price (BIGINT)",
    )

    assert "total revenue for each product" in prompt
    assert "Table: sales" in prompt
    assert "quantity" in prompt
    assert "SQLite" in prompt
    assert "read-only SELECT" in prompt


def test_prompt_requires_sql_only():
    prompt = build_sql_prompt(
        question="Show all products",
        schema_context="Table: sales\n  - product (TEXT)",
    )

    assert "without Markdown fences" in prompt
    assert "CANNOT_ANSWER" in prompt


