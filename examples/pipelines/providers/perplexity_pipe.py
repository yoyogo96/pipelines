from typing import List, Union, Generator, Iterator
from pydantic import BaseModel
import os
import requests
from utils.pipelines.main import pop_system_message

class Pipeline:
    class Valves(BaseModel):
        PERPLEXITY_API_BASE_URL: str = "https://api.perplexity.ai"
        PERPLEXITY_API_KEY: str = ""

    def __init__(self):
        self.type = "manifold"
        self.name = "Perplexity: "
        self.valves = self.Valves(
            **{
                "PERPLEXITY_API_KEY": os.getenv(
                    "PERPLEXITY_API_KEY", "your-perplexity-api-key-here"
                )
            }
        )
        print(f"Loaded API Key: {self.valves.PERPLEXITY_API_KEY}")

        self.pipelines = [
            {"id": "sonar-pro", "name": "sonar-pro"},
            {"id": "sonar-deep-research", "name": "sonar-deep-research"},
            {"id": "sonar-reasoning", "name": "sonar-reasoning"},
            {"id": "sonar-reasoning-pro", "name": "sonar-reasoning-pro"},
            {"id": "r1-1776", "name": "r1-1776"},
        ]

    async def on_startup(self):
        print(f"on_startup:{__name__}")

    async def on_shutdown(self):
        print(f"on_shutdown:{__name__}")

    async def on_valves_updated(self):
        print(f"on_valves_updated:{__name__}")

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        print(f"pipe:{__name__}")

        system_message, messages = pop_system_message(messages)
        system_prompt = "You are a helpful assistant."
        if system_message is not None:
            system_prompt = system_message["content"]

        headers = {
            "Authorization": f"Bearer {self.valves.PERPLEXITY_API_KEY}",
            "Content-Type": "application/json",
            "accept": "application/json"
        }

        payload = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                *messages
            ],
            "stream": body.get("stream", True),
            "return_citations": True,
            "return_images": True
        }

        response = requests.post(
            f"{self.valves.PERPLEXITY_API_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            stream=payload["stream"]
        )

        if response.status_code != 200:
            raise Exception(f"Perplexity API Error: {response.status_code} - {response.text}")

        if payload["stream"]:
            for line in response.iter_lines():
                if line:
                    yield line.decode("utf-8")
        else:
            return response.json()["choices"][0]["message"]["content"]
