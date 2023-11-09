# coding: utf-8

"""
    Muyu
"""

import os
import sys
import re
import codecs
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
sys.path.append(here)

def read(*parts):
    with codecs.open(os.path.join(here, *parts), "r") as fp:
        return fp.read()
    
def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

version = find_version('muyu', '__init__.py')

install_requires = []
with open(os.path.join(here, 'requirements.txt')) as f:
    for r in [x.strip() for x in f.readlines()]:
        if r != '':
            install_requires.append(r)

setup(
    name='muyu',
    version=version,
    packages=find_packages(),
    package_data={
        #'webui': ['**/*']
    },
    install_requires = install_requires,
    scripts=['setup.py', './scripts/muyu', 'requirements.txt'],
)