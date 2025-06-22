import anthropic
import dotenv
import os
from io import BytesIO

dotenv.load_dotenv()


class LlmClient:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def upload_file(self, filename: str, file_type: str, content: BytesIO) -> str:
        file_meta = self.client.beta.files.upload(
            file=(os.path.basename(filename), content, file_type)
        )
        return file_meta.id

    def delete_file(self, file_id: str):
        self.client.beta.files.delete(file_id)


llm = LlmClient()
