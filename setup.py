# coding: utf-8

"""
    Myla
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

version = find_version('myla', '__init__.py')

install_requires = []
with open(os.path.join(here, 'requirements.txt')) as f:
    for r in [x.strip() for x in f.readlines()]:
        if r != '':
            install_requires.append(r)

extras_require = {
    'all': [
        'sentence_transformers',
        'lancedb',
        'faiss-cpu',
        'chatglm_cpp>=0.3.0',
    ],
    'lancedb': [
        'sentence_transformers',
        'lancedb',
    ],
    'faiss-cpu': [
        'sentence_transformers',
        'faiss-cpu',
        'langchain'
    ],
    'faiss-gpu': [
        'sentence_transformers',
        'faiss-gpu',
        'langchain'
    ],
    'chatglm': [
        'chatglm_cpp>=0.3.0'
    ]
}

setup(
    python_requires=">=3.9",
    name='myla',
    version=version,
    description="A local implementation of OpenAI Assistants API: Myla stands for MY Local Assistant",
    author_email="shenggong.wang@gmail.com",
    url="https://github.com/muyuworks/myla",
    keywords=["AI assistant", "LLM", "Myla", "chatbot"],
    long_description_content_type="text/markdown",
    long_description=read("README.md"),
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    package_data={
        '': ['webui/**']
    },
    install_requires = install_requires,
    extras_require=extras_require,
    scripts=['./scripts/myla'],
)