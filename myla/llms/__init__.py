import os
from .backend import LLM

def get(model_name=None):
    """
    Get LLM
    """
    if not model_name:
        model_name = os.environ.get("DEFAULT_LLM_MODEL_NAME")

    if not model_name:
        raise ValueError(f"Invalid LLM backend: {model_name}, you should set DEFAULT_LLM_MODEL_NAME in environment variables.")

    idx = model_name.find("@")

    backend = model_name[:idx] if idx != -1 else "openai"
    model = model_name[idx+1:] if idx != -1 else model_name

    if backend == "openai":
        from .openai import OpenAI
        return OpenAI(model=model)
    elif backend == "chatglm":
        from .chatglm import ChatGLM
        return ChatGLM(model=model)
    else:
        raise ValueError(f"Invalid LLM backend: {model_name}")
