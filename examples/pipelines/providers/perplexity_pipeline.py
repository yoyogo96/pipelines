import os
import requests
from typing import List, Union, Generator, Iterator
from pydantic import BaseModel

class Pipeline:
    class Valves(BaseModel):
        PERPLEXITY_API_KEY: str = ""

    def __init__(self):
        self.type = "manifold"
        self.id = "perplexity"
        self.name = "perplexity/"

        self.valves = self.Valves(
            **{"PERPLEXITY_API_KEY": os.getenv("PERPLEXITY_API_KEY", "your-api-key-here")}
        )
        self.base_url = "https://api.perplexity.ai/v1"

    def get_perplexity_models(self):
        # In the future, this could fetch models dynamically from Perplexity AI
        return [
            {"id": "llama-3-sonar-large-32k-online", "name": "LLaMA-3 Sonar Large"},
            # Add other Perplexity models here as they become available
        ]

    async def on_startup(self):
        print(f"on_startup:{__name__}")
        pass

    async def on_shutdown(self):
        print(f"on_shutdown:{__name__}")
        pass

    async def on_valves_updated(self):
        # This function is called when the valves are updated.
        pass

    # Pipelines are the models that are available in the manifold.
    # It can be a list or a function that returns a list.
    def pipelines(self) -> List[dict]:
        return self.get_perplexity_models()

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        try:
            if "user" in body:
                del body["user"]
            if "chat_id" in body:
                del body["chat_id"]
            if "title" in body:
                del body["title"]

            if body.get("stream", False):
                return self.stream_response(model_id, messages, body)
            else:
                return self.get_completion(model_id, messages, body)
        except requests.exceptions.RequestException as e:
            return f"Error: {e}"

    def stream_response(
        self, model_id: str, messages: List[dict], body: dict
    ) -> Generator:
        max_tokens = (
            body.get("max_tokens") if body.get("max_tokens") is not None else 4096
        )
        temperature = (
            body.get("temperature") if body.get("temperature") is not None else 0.8
        )
        top_k = body.get("top_k") if body.get("top_k") is not None else 40
        top_p = body.get("top_p") if body.get("top_p") is not None else 0.9
        stop_sequences = body.get("stop") if body.get("stop") is not None else []

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.valves.PERPLEXITY_API_KEY}"},
            json={
                "model": model_id,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_k": top_k,
                "top_p": top_p,
                "stop": stop_sequences,
                "stream": True,
            },
            stream=True,
        )

        for line in response.iter_lines():
            if line:
                chunk = line.decode("utf-8")
                yield chunk

    def get_completion(self, model_id: str, messages: List[dict], body: dict) -> str:
        max_tokens = (
            body.get("max_tokens") if body.get("max_tokens") is not None else 4096
        )
       
