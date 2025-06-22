from models import AnsciOutline
import anthropic
from dotenv import load_dotenv
import os
import base64
import httpx
import json

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

def generate_outline(history: list[dict]) -> AnsciOutline | None:
    """
    Generate an outline for the animation from message history. We make sure
    that the history contains the paper as a file, and user messages.

    """
    response = client.messages.create(
        model="claude-3-5-haiku-latest",
        max_tokens=1024,
        system="You are a seasoned educator.", # <-- role prompt
        messages=history,
        tools = [
            {
                    "name": "generate_animation_from_outline",
                    "description": "Generate an animation from an outline",
                    "input_schema": AnsciOutline.model_json_schema()
            }
        ],

    )
    
    # Check if there's a tool call in the response
    if len(response.content) > 1 and hasattr(response.content[1], 'input'):
        # Parse the tool call input into AnsciOutline object
        tool_input = response.content[1].input
        if isinstance(tool_input, str):
            tool_input = json.loads(tool_input)
        
        return (response.content[0].text, AnsciOutline(**tool_input))
    
    return (response.content[0].text, None)
    


pdf_url = "https://www.cs.cmu.edu/~conitzer/visualAMM.pdf"
pdf_data = base64.standard_b64encode(httpx.get(pdf_url).content).decode("utf-8")

history=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_data
                    }
                },
                {
                    "type": "text",
                    "text": "Can you summarize the paper briefly?"
                }
            ]
        }
    ]


if __name__ == "__main__":
    print(generate_outline(history))