import os
from typing import Dict, List

import openai

from .. import utils
from .backend import LLM


class OpenAI(LLM):
    def __init__(self, model=None, api_key=None, base_url=None) -> None:
        super().__init__(model)
        self.api_key = api_key
        self.base_url = base_url

    async def chat(self, messages: List[Dict], model=None, stream=False, **kwargs):
        if "api_key" not in kwargs:
            kwargs["api_key"] = self.api_key
        if "base_url" not in kwargs:
            kwargs["base_url"] = self.base_url

        return await chat(
            messages=messages,
            model=model if model else self.model,
            stream=stream,
            **kwargs
        )

    async def generate(self, instructions: str, model=None, stream=False, **kwargs):
        if not model:
            model = self.model
        return await generate(instructions=instructions, model=model, stream=stream, **kwargs)

    def sync_chat(self, messages: List[Dict], model=None, stream=False, **kwargs):
        if "api_key" not in kwargs:
            kwargs["api_key"] = self.api_key
        if "base_url" not in kwargs:
            kwargs["base_url"] = self.base_url

        return sync_chat(
            messages=messages,
            model=model if model else self.model,
            stream=stream,
            **kwargs
        )

    def sync_generate(self, instructions: str, model=None, stream=False, **kwargs):
        if not model:
            model = self.model
        return sync_generate(instructions=instructions, model=model, stream=stream, **kwargs)


async def chat(messages: List[Dict], model=None, stream=False, api_key=None, base_url=None, **kwargs):
    if not api_key:
        api_key = os.environ.get("LLM_API_KEY")
    if not base_url:
        base_url = os.environ.get("LLM_ENDPOINT")
    if not model:
        model = os.environ.get("DEFAULT_LLM_MODEL_NAME")

    llm = openai.AsyncOpenAI(api_key=api_key, base_url=base_url)

    usage = None
    if "usage" in kwargs:
        usage = kwargs.pop("usage")

    @utils.retry
    async def _call():
        resp = await llm.chat.completions.create(
            model=model,
            messages=messages,
            stream=stream,
            **kwargs
        )
        if stream:
            async def iter():
                async for r in resp:
                    yield r.choices[0].delta.content if r.choices else 'Unexpected LLM error, possibly due to context being too long.'
            return iter()
        else:
            genereated = resp.choices[0].message.content
            if usage:
                usage.prompt_tokens = resp.usage.prompt_tokens
                usage.completion_tokens = resp.usage.completion_tokens
            return genereated

    return await _call()


async def generate(instructions: str, model=None, stream=False, **kwargs):
    r = await chat(messages=[{
        "role": "system",
        "content": instructions
    }], model=model, stream=stream, **kwargs)
    return r


def sync_chat(messages: List[Dict], model=None, stream=False, api_key=None, base_url=None, **kwargs):
    if not api_key:
        api_key = os.environ.get("LLM_API_KEY")
    if not base_url:
        base_url = os.environ.get("LLM_ENDPOINT")
    if not model:
        model = os.environ.get("DEFAULT_LLM_MODEL_NAME")

    llm = openai.OpenAI(api_key=api_key, base_url=base_url)

    usage = None
    if "usage" in kwargs:
        usage = kwargs.pop("usage")

    @utils.retry
    def _call():
        resp = llm.chat.completions.create(
            model=model,
            messages=messages,
            stream=stream,
            **kwargs
        )
        if stream:
            def iter():
                for r in resp:
                    yield r.choices[0].delta.content if r.choices else 'Unexpected LLM error, possibly due to context being too long.'
            return iter()
        else:
            genereated = resp.choices[0].message.content
            if usage:
                usage.prompt_tokens = resp.usage.prompt_tokens
                usage.completion_tokens = resp.usage.completion_tokens
            return genereated

    return _call()


def sync_generate(instructions: str, model=None, stream=False, **kwargs):
    r = sync_chat(messages=[{
        "role": "system",
        "content": instructions
    }], model=model, stream=stream, **kwargs)
    return r
