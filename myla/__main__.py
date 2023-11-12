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

    if args.extentions:
        ext_dir = os.path.abspath(args.extentions)
        os.environ['EXT_DIR'] = ext_dir

        if args.reload:
            if not args.reload_dirs:
                args.reload_dirs = []
                args.reload_dirs.append(MYLA_LIB_DIR)
            args.reload_dirs.append(ext_dir)

    if args.vectorstore:
        os.environ['VECTORSTORE_DIR'] = args.vectorstore

    uvicorn.run('myla:entry', host=args.host, port=args.port,
                workers=args.workers, reload=args.reload, h11_max_incomplete_event_size=0,
                log_config=LOGGING_CONFIG, reload_dirs=args.reload_dirs)


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
parser.add_argument("--extentions", default=None, help="extentions directory")
parser.add_argument("--vectorstore", default=None,
                    help="vectorstore directory")
parser.add_argument("--debug", default=False,
                    action='store_true', help="enable debug")


def main():
    args = parser.parse_args(sys.argv[1:])

    if os.path.exists(args.env_file):
        from dotenv import load_dotenv
        load_dotenv(args.env_file)

    runserver(args)


main()
