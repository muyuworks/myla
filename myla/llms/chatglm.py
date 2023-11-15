import os
from typing import Dict, List
from .backend import LLM
from . import utils

from chatglm_cpp import Pipeline

class ChatGLM(LLM):
    def __init__(self, model=None) -> None:
        super().__init__(model)

    async def chat(self, messages: List[Dict], model=None, stream=False, **kwargs):
        if not model:
            model = self.model
        return await chat(messages=messages, model=model, stream=stream)
    
    async def generate(self, instructions: str, model=None, stream=False, **kwargs):
        if not model:
            model = self.model
        return await generate(instructions=instructions, model=model, stream=stream, **kwargs)

async def chat(messages: List[Dict], model=None, stream=False, **kwargs):
    if not model:
        model = os.environ.get("DEFAULT_LLM_MODEL_NAME")

    pipeline = Pipeline(model)
    history = []
    for m in messages:
        history.append(f"{m['content']}")
    #history.append("assistant: ")
    
    g = pipeline.chat(
        history=history,
        stream=True,
    **kwargs)
    if stream:
        async def iter():
            for c in g:
                yield c
        return iter()
    else:
        genreated = []
        for c in g:
            genreated.append(c)
        return ''.join(genreated)
    
async def generate(instructions: str, model=None, stream=False, **kwargs):
    r = await chat(messages=[{
        "role": "system",
        "content": instructions
    }], model=model, stream=stream, **kwargs)
    return r