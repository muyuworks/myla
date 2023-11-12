import os
from typing import List, Dict
import openai
from . import utils

def plain_messages(messages: List[Dict], model=None):
    text = []
    for m in messages:
        role = m['role']
        text.append(f"{role}: {m['content']}")
    return '\n'.join(text)

async def chat_complete(messages: List[Dict], model=None, stream=False, **kwargs):
    if 'api_key' not in kwargs:
        api_key = os.environ.get("LLM_API_KEY")
    if 'base_url' not in kwargs:
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
            return resp
        else:
            genereated = resp.choices[0].message.content
            return genereated
    
    return await _call()

async def complete(instructions: str, **kwargs):
    r = await chat_complete(messages=[{
        "role": "system",
        "content": instructions
    }], **kwargs)
    return r
