import os
import sys
import importlib
from starlette.applications import Starlette
from starlette.responses import RedirectResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from contextlib import asynccontextmanager

from .persistence import Persistence
from ._run_scheduler import RunScheduler
from . import _tools
from . import _env
from ._api import api
from .webui._web_template import render, get_templates
from ._logging import logger
from .vectorstores import load_loaders
from . import webui
from . import users
from . import _auth
from . import _version


def import_extensions():
    ext_dir = os.environ.get("EXT_DIR")
    if ext_dir:
        sys.path.append(ext_dir)

        entry_py = os.path.join(ext_dir, 'entry.py')
        if os.path.exists(entry_py):
            importlib.import_module('entry')


@asynccontextmanager
async def lifespan(app: Starlette):
    try:
        # Load extensions
        import_extensions()

        # Load tools
        _tools.load_tools()

        # Load loaders
        load_loaders()

        # Initialize database
        Persistence.default().initialize_database()

        # Create default super admin user
        sa = users.create_default_superadmin()
        if sa:
            logger.warn(f"Super admin user created: {sa.username}")

        # Start RunScheduler
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
        '/webui/statics',
        name='statics',
        app=StaticFiles(directory=os.path.join(_env.webui_dir(), 'statics'), check_dir=False),
    ),
    Route(
        '/webui/',
        name='webui',
        endpoint=render('index.html', context={'version': _version.VERSION})
    ),
    Route(
        '/',
        name='home',
        endpoint=lambda r: RedirectResponse('/webui')
    ),
    Route(
        '/assistants/{assistant_id}',
        name='assistant',
        endpoint=webui.assistant
    )
]

# Middlewares
middleware = [
    Middleware(AuthenticationMiddleware, backend=_auth.BasicAuthBackend())
]

entry = Starlette(debug=False, routes=routes, middleware=middleware, lifespan=lifespan)


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
