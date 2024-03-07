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
