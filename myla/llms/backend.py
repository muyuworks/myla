from typing import Dict, List


class LLM:
    def __init__(self, model=None) -> None:
        self.model = model

    async def chat(self, messages: List[Dict], model=None, stream=False, **kwargs):
        raise NotImplemented()

    async def generate(self, instructions: str, model=None, stream=False, **kwargs):
        raise NotImplemented()

    def sync_chat(self, messages: List[Dict], model=None, stream=False, **kwargs):
        raise NotImplemented()

    def sync_generate(self, instructions: str, model=None, stream=False, **kwargs):
        raise NotImplemented()


class Usage:
    def __init__(self, prompt_tokens: int = 0, completion_tokens: int = 0) -> None:
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
