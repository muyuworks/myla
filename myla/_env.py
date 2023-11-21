import os

_here = os.path.abspath(os.path.join(os.path.dirname(__file__)))

def webui_dir():
    "Returns the directory where webuid resources ared stored."
    return os.path.join(_here, 'webui')
