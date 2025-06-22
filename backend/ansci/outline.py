from .models import AnsciOutline
from anthropic.types import MessageParam
import anthropic
import os
import base64
import httpx
import json

# Load API key directly from environment
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    # Try loading from .env file manually
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith("ANTHROPIC_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break

client = anthropic.Anthropic(api_key=api_key)


def generate_outline(history: list[MessageParam]) -> tuple[str, AnsciOutline | None]:
    """
    Generate an outline for the animation from message history. We make sure
    that the history contains the paper as a file, and user messages.
    """
    response = client.messages.create(
        max_tokens=32000,  # Maximum tokens for Sonnet 4
        model="claude-sonnet-4-20250514",  # Use Sonnet 4 for higher quality outlines
        system="You are a seasoned educator.",  # <-- role prompt
        stream=True,  # Enable streaming for long requests
        messages=history,
        tools=[
            {
                "name": "generate_animation_from_outline",
                "description": "Generate an animation from an outline",
                "input_schema": AnsciOutline.model_json_schema(),
            }
        ],
    )

    # Collect streamed response
    text_content = ""
    tool_call = None
    tool_input_json = ""

    for chunk in response:
        if chunk.type == "content_block_start":
            if chunk.content_block.type == "text":
                pass  # Text block started
            elif chunk.content_block.type == "tool_use":
                tool_call = chunk.content_block
        elif chunk.type == "content_block_delta":
            if chunk.delta.type == "text_delta":
                text_content += chunk.delta.text
            elif chunk.delta.type == "input_json_delta":
                # Accumulate tool input JSON
                tool_input_json += chunk.delta.partial_json
        elif chunk.type == "content_block_stop":
            pass  # Block completed

    # Check if there's a tool call in the response
    if tool_call and tool_input_json:
        # Parse the accumulated tool call input into AnsciOutline object
        try:
            tool_input = json.loads(tool_input_json)
            return (text_content, AnsciOutline(**tool_input))
        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠️ Failed to parse tool input: {e}")
            return (text_content, None)

    return (text_content, None)


if __name__ == "__main__":
    pdf_url = "https://www.cs.cmu.edu/~conitzer/visualAMM.pdf"
    pdf_data = base64.standard_b64encode(httpx.get(pdf_url).content).decode("utf-8")

    history: list[MessageParam] = [
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_data,
                    },
                },
                {"type": "text", "text": "Can you summarize the paper briefly?"},
            ],
        }
    ]
    print(generate_outline(history))
