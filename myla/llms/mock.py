from typing import Dict, List
from .backend import LLM


class MockLLM(LLM):
    def __init__(self) -> None:
        super().__init__()

    async def chat(self, messages: List[Dict], model=None, stream=False, **kwargs):
        last_message = messages[-1]['content']

        if stream:
            async def iter():
                for c in [last_message]:
                    yield c
            return iter()
        else:
            return last_message

    async def generate(self, instructions: str, model=None, stream=False, **kwargs):
        return instructions
