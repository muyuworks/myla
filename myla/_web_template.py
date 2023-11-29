import os
from starlette.templating import Jinja2Templates
from jinja2.exceptions import TemplateNotFound
from starlette.exceptions import HTTPException
from ._env import webui_dir


def get_templates(templates_dir=None):
    if not templates_dir:
        templates_dir = webui_dir()
    return Jinja2Templates(directory=os.path.join(templates_dir, 'templates'))


_templates = get_templates()


def render(template_name, context={}, templates=None):
    """Render a template."""
    if not templates:
        templates = _templates

    async def _request(request):
        context['request'] = request
        try:
            return templates.TemplateResponse(template_name, context=context)
        except TemplateNotFound as e:
            raise HTTPException(status_code=404, detail=f"Template not found: {e}")
    return _request
