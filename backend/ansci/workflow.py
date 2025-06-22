from io import BytesIO
import base64

from .outline import generate_outline
from .animate import create_ansci_animation
from .service import llm


def create_animation(file: BytesIO, filename: str, prompt: str | None = None):
    if prompt is None:
        prompt = "Create an animation for the paper."

    pdf_data = base64.b64encode(file.read()).decode("utf-8")

    history = [
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
                {
                    "type": "text",
                    "text": prompt,
                },
            ],
        },
    ]

    outline = generate_outline(history)
    if outline is not None:
        animation = create_ansci_animation(history, outline)
        return animation
