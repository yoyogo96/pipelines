from typing import List, Union, Generator, Iterator
from schemas import OpenAIChatMessage
from pydantic import BaseModel
import os
import requests


class Pipeline:
    class Valves(BaseModel):
        PERPLEXITY_API_KEY: str = ""

    def __init__(self):
        # Optionally, you can set the id and name of the pipeline.
        # Best practice is to not specify the id so that it can be automatically inferred from the filename, so that users can install multiple versions of the same pipeline.
        # The identifier must be unique across all pipelines.
        # The identifier must be an alphanumeric string that can include underscores or hyphens. It cannot contain spaces, special characters, slashes, or backslashes.
        # self.id = "perplexity_pipeline"
        self.name = "Perplexity Pipeline"
        self.valves = self.Valves(
            **{
                "PERPLEXITY_API_KEY": os.getenv(
                    "PERPLEXITY_API_KEY", "your-perplexity-api-key-here"
                )
            }
        )

    async def on_startup(self):
        # This function is called when the server is started.
        print(f"on_startup:{__name__}")

    async def on_shutdown(self):
        # This function is called when the server is stopped.
        print(f"on_shutdown:{__name__}")

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        # This is where you can add your custom pipelines like RAG.
        print(f"pipe:{__name__}")

        print(messages)
        print(user_message)

        PERPLEXITY_API_KEY = self.valves.PERPLEXITY_API_KEY
        MODEL = model_id  # The model ID should be passed as an argument

        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {**body, "model": MODEL}

        if "user" in payload:
            del payload["user"]
        if "chat_id" in payload:
            del payload["chat_id"]
        if "title" in payload:
            del payload["title"]

        print(payload)

        try:
            r = requests.post(
                url="https://api.perplexity.ai/v1/chat/completions",
                json=payload,
                headers=headers,
                stream=True,
            )

            r.raise_for_status()

            if body.get("stream", False):
                return r.iter_lines()
            else:
                return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error: {e}"

# Example usage:
api_key = "YOUR_PERPLEXITY_API_KEY"
pipeline = Pipeline()
user_message = "Tell me a joke."
model_id = "llama-3-sonar-large-32k-online"
messages = [
    {"role": "system", "content": "You are an AI assistant."},
    {"role": "user", "content": user_message}
]
body = {"messages": messages, "stream": False}

response = pipeline.pipe(user_message, model_id, messages, body)
print(response)

# For streaming response:
body_stream = {"messages": messages, "stream": True}
response_stream = pipeline.pipe(user_message, model_id, messages, body_stream)
for res in response_stream:
    print(res)
