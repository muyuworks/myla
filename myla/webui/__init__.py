from .._web_template import render
from starlette.requests import Request


async def assistant(request: Request):
    ctx = {
        "assistant_id": request.path_params.get("assistant_id", ''),
        "chat_mode": True
    }
    return await render('index.html', context=ctx)(request=request)