
from app.services.llm_client import generate_sql
from app.services.schema_context import build_schema_context

schema = build_schema_context()

question = "What is the total revenue for each product?"

sql = generate_sql(
    question=question,
    schema_context=schema,
)

print("\nQuestion:")
print(question)

print("\nGenerated SQL:")
print(sql)
