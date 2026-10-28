from app.services.llm_client import get_groq_client

def test_groq_client_initializes():
    client = get_groq_client()
    assert client is not None