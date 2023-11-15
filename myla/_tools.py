import os
import json
import importlib
from ._logging import logger

_tools = {}

def load_tools():
    tools = os.environ.get('TOOLS')
    try:
        if tools:
            tools = json.loads(tools)
            for tool in tools:
                impl = tool['impl']
                ss = impl.split('.')
                module = importlib.import_module('.'.join(ss[:-1]))

                args = tool['args'] if 'args' in tool else {}
                instance = getattr(module, ss[-1])(**args)
                _tools[tool["name"]] = instance
    except Exception as e:
        logger.error(f"Load tools faild: {tools}", exc_info=e)


def get_tool(name):
    return _tools.get(name)

def get_tools():
    return _tools