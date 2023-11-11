import os
import logging

logger = logging.getLogger('muyu')

def is_debug_enabled():
    return os.environ.get("DEBUG") == True

def debug(*args, **kargs):
    if is_debug_enabled():
        logger.debug(*args, **kargs)

def info(*args, **kwargs):
    logger.info(*args, **kwargs)