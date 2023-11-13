import os
from typing import Dict, List
import openai
from .backend import LLM
from .. import utils


class OpenAI(LLM):
    def __init__(self, model=None, api_key=None, base_url=None) -> None:
        super().__init__(model)
        self.api_key = api_key
        self.base_url = base_url

    async def chat(self, messages: List[Dict], model=None, stream=False, **kwargs):
        return await chat(
            messages=messages,
            model=model if model else self.model,
            stream=stream,
            api_key=self.api_key,
            base_url=self.base_url,
            **kwargs
        )
    
    async def generate(self, instructions: str, model=None, stream=False, **kwargs):
        if not model:
            model = self.model
        return await generate(instructions=instructions, model=model, stream=stream, **kwargs)


async def chat(messages: List[Dict], model=None, stream=False, api_key=None, base_url=None, **kwargs):
    if not api_key:
        api_key = os.environ.get("LLM_API_KEY")
    if not base_url:
        base_url = os.environ.get("LLM_ENDPOINT")
    if not model:
        model = os.environ.get("DEFAULT_LLM_MODEL_NAME")

    llm = openai.AsyncOpenAI(api_key=api_key, base_url=base_url)

    @utils.retry
    async def _call():
        resp = await llm.chat.completions.create(
            model=model,
            messages=messages,
            stream=stream,
            timeout=120,
            **kwargs
        )
        if stream:
            async def iter():
                async for r in resp:
                    yield r.choices[0].delta.content
            return iter()
        else:
            genereated = resp.choices[0].message.content
            return genereated

    return await _call()


async def generate(instructions: str, model=None, stream=False, **kwargs):
    r = await chat(messages=[{
        "role": "system",
        "content": instructions
    }], model=model, stream=stream, **kwargs)
    return r
