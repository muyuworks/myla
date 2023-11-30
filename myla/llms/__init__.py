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
    elif backend == "mock":
        from .mock import MockLLM
        return MockLLM()
    else:
        raise ValueError(f"Invalid LLM backend: {model_name}")


def list_models():
    """List all models."""
    models = {}

    if os.environ.get("LLM_ENDPOINT"):
        endpoint = os.environ.get("LLM_ENDPOINT")
        api_key = os.environ.get("LLM_API_KEY")
        import openai
        client = openai.OpenAI(api_key=api_key, base_url=endpoint)
        openai_models = client.models.list()
        for m in openai_models.data:
            models[m.id] = m

    default_model = os.environ.get("DEFAULT_LLM_MODEL_NAME")
    if default_model and default_model not in models:
        models[default_model] = {
            'id': default_model,
            'object': 'model'
        }

    return models
