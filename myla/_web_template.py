import os
from starlette.templating import Jinja2Templates
from jinja2.exceptions import TemplateNotFound
from starlette.exceptions import HTTPException
from ._env import webui_dir

templates = Jinja2Templates(directory=os.path.join(webui_dir(), 'templates'))

def render(template_name, context = {}):
    """Render a template."""
    async def _request(request):
        context['request'] = request
        try:
            return templates.TemplateResponse(template_name, context=context)
        except TemplateNotFound as e:
            raise HTTPException(status_code=404, detail=f"Template not found: {e}")
    return _request