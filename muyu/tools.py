import os
import json
import importlib

_tools = {}

def load_tools():
    tools = os.environ.get('TOOLS')
    if tools:
        tools = json.loads(tools)
        for tool in tools:
            impl = tool['impl']
            ss = impl.split('.')
            module = importlib.import_module('.'.join(ss[:-1]))

            args = tool['args'] if 'args' in tool else {}
            instance = getattr(module, ss[-1])(**args)
            _tools[tool["name"]] = instance

def get_tool(name):
    return _tools.get(name)

def get_tools():
    return _tools