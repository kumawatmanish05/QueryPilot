
from app.services.llm_client import get_groq_client

client = get_groq_client()

response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "user",
            "content": "Reply with exactly: QueryPilot connected!"
        }
    ],
    temperature=0,
    max_completion_tokens=50,
)

print(response.choices[0].message.content)
