
import os

from dotenv import load_dotenv
from groq import Groq

from app.services.prompt_builder import build_sql_prompt

load_dotenv()


def get_groq_client() -> Groq:
    """Create a Groq client using the API key from .env."""
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Add it to your local .env file."
        )

    return Groq(api_key=api_key)


def generate_sql(question: str, schema_context: str) -> str:
    """Generate a SQL query from a natural-language question."""
    prompt = build_sql_prompt(question, schema_context)
    client = get_groq_client()

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0,
        max_completion_tokens=300,
    )

    sql = response.choices[0].message.content

    if not sql:
        raise RuntimeError("The language model returned an empty response.")

    return sql.strip()

