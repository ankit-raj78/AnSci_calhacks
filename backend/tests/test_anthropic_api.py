from re import S
import anthropic
import os

import dotenv

dotenv.load_dotenv()


def test_anthropic_api():
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=100,
        messages=[{"role": "user", "content": "Hello, world!"}],
    )
    print(response)


test_anthropic_api()
