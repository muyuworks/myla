#!/usr/bin/env python
import os
import sys
import argparse
import uvicorn
from uvicorn.config import LOGGING_CONFIG

MYLA_LIB_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.pardir))
sys.path.insert(0, MYLA_LIB_DIR)


def runserver(args):
    log_level = "DEBUG" if args.debug else "INFO"
    logger = {"handlers": ["default"], "level": log_level, "propagate": False}
    LOGGING_CONFIG['loggers'][''] = logger
    LOGGING_CONFIG['loggers']['myla'] = logger

    reload_dirs = []
    ext_dir = None

    if args.extensions:
        ext_dir = os.path.abspath(args.extensions)
        os.environ['EXT_DIR'] = ext_dir

    if args.reload:
        reload_dirs.append(MYLA_LIB_DIR)
        if ext_dir:
            reload_dirs.append(ext_dir)
        if args.reload_dirs:
            reload_dirs.append(args.relead_dirs)

    if args.data:
        os.environ['DATA_DIR'] = args.data

    if args.vectorstore:
        os.environ['VECTORSTORE_DIR'] = args.vectorstore
    elif 'DATA_DIR' in os.environ:
        os.environ['VECTORSTORE_DIR'] = os.path.join(os.environ['DATA_DIR'], 'vectorstore')

    uvicorn.run('myla:entry', host=args.host, port=args.port,
                workers=args.workers, reload=args.reload, h11_max_incomplete_event_size=0,
                log_config=LOGGING_CONFIG, reload_dirs=reload_dirs)


parser = argparse.ArgumentParser()

parser.add_argument('-H', '--host', default='0.0.0.0',
                    help="bind socket to this host. default: 0.0.0.0")
parser.add_argument('-p', '--port', default=2000,
                    type=int, help="bind socket to this port, default: 2000")
parser.add_argument('-w', '--workers', default=1, type=int,
                    help="number of worker processes, default: 1")
parser.add_argument('-r', '--reload', default=False,
                    action='store_true', help="enable auto-reload")
parser.add_argument('--reload-dirs', default=None,
                    help="set reload directories explicitly, default is applications directory")
parser.add_argument('--env-file', default='.env',
                    help="environment configuration file")
parser.add_argument("--extensions", default=None, help="extensions directory")
parser.add_argument("--vectorstore", default=None,
                    help="vectorstore directory")
parser.add_argument("--data", default='data',
                    help="data directory")
parser.add_argument("--debug", default=False,
                    action='store_true', help="enable debug")


def main():
    args = parser.parse_args(sys.argv[1:])

    if os.path.exists(args.env_file):
        from dotenv import load_dotenv
        load_dotenv(args.env_file)

    runserver(args)


main()
