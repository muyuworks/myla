import os
import sys
import importlib
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
from ._web_template import render, get_templates
from ._logging import logger
from .vectorstores import load_loaders
from . import webui


def import_extensions():
    ext_dir = os.environ.get("EXT_DIR")
    if ext_dir:
        sys.path.append(ext_dir)

        entry_py = os.path.join(ext_dir, 'entry.py')
        if os.path.exists(entry_py):
            importlib.import_module('entry')


@asynccontextmanager
async def lifespan(api: FastAPI):
    try:
        # Load extensions
        import_extensions()

        # Load tools
        _tools.load_tools()

        # Load loaders
        load_loaders()

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
    ),
    Route(
        '/assistants/{assistant_id}',
        name='assistant',
        endpoint=webui.assistant
    )
]

entry = Starlette(debug=False, routes=routes, lifespan=lifespan)


def register(path, name, endpoint):
    entry.routes.insert(0, Route(path=path, name=name, endpoint=endpoint))


def register_webui(webui_dir):
    webui_dir = os.path.abspath(webui_dir)
    templates = get_templates(webui_dir)

    entry.routes.insert(0, Mount(
        '/static',
        name='static',
        app=StaticFiles(directory=os.path.join(webui_dir, 'static'), check_dir=False),
    ))

    entry.routes.insert(0, Route(
        '/',
        name='home',
        endpoint=render('index.html', templates=templates)
    ))
