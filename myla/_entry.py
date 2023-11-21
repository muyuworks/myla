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
from ._logging import logger

@asynccontextmanager
async def lifespan(api: FastAPI):
    try:
        # Load tools
        ext_dir = os.environ.get("EXT_DIR")
        if ext_dir:
            sys.path.append(ext_dir)
        
        _tools.load_tools()

        # on startup
        Persistence.default().initialize_database()
        RunScheduler.default().start()

    except Exception as e:
        logger.error(f"Lifespan error: {e}", exc_info=e)
    finally:
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