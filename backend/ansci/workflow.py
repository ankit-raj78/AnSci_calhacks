from io import BytesIO

from .outline import generate_outline
from .animate import create_ansci_animation
from .service import llm


def create_animation(file: BytesIO, filename: str, prompt: str | None = None):
    try:
        file_id = llm.upload_file(filename, "application/pdf", file)

        if prompt is None:
            prompt = "Create an animation for the paper."

        history = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "file",
                            "file_id": file_id,
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
    finally:
        llm.delete_file(file_id)
