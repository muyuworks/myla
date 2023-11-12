import os
import sys
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from fastapi import FastAPI
from contextlib import asynccontextmanager

from .persistence import Persistence
from ._run_scheduler import RunScheduler
from . import _tools
from . import _env
from ._api import api
from ._web_template import render

@asynccontextmanager
async def lifespan(api: FastAPI):
    ext_dir = os.environ.get("EXT_DIR")
    if ext_dir:
        sys.path.append(ext_dir)
    
    _tools.load_tools()

    # on startup
    Persistence.default().initialize_database()
    await RunScheduler.default().start()

    yield
    # on shutdown
    pass

# Routes
routes = [
    Mount(
        '/api',
        name='api',
        app=api
    ),
    Mount(
        '/static',
        name='static',
        app=StaticFiles(directory=os.path.join(_env.webui_dir(), 'static'), check_dir=False),
    ),
    Route(
        '/',
        name='home',
        endpoint=render('index.html')
    )
]

entry = Starlette(debug=False, routes=routes, lifespan=lifespan)