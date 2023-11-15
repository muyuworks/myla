[English](README.md) | [简体中文](README_zh_CN.md)

# Myla: MY Local Assistants

## Self-hosting AI Assistants compatible with OpenAI

Myla stands for MY Local Assistants and is designed and optimized for deploying AI assistants based on large language models (LLMs) in a private environment. Myla provides an API compatible with the **OpenAI assistants API**, with support for multiple LLM backends. Whether on a laptop or a production server, you can quickly develop and run AI assistants.

## Quick Start
### Installation

Python version requirement: <= 3.11

Myla can be installed from PyPI using `pip`. It is recommended to create a new virtual environment before installation to avoid conflicts.

```bash
pip install myla
```

### Configuration

Myla supports using an OpenAI API-compatible LLM service as the backend. You can use the OpenAI API directly or deploy your own local LLM. If you want to deploy a local LLM, it is recommended to use [Xorbits Inference](https://github.com/xorbitsai/inference).

Create a `.env` file in the current directory with the following content:

```
# Database configuration
DATABASE_URL=sqlite:///myla.db
DATABASE_CONNECT_ARGS={"check_same_thread": false}

# LLM configuration
LLM_ENDPOINT=https://api.openai.com/v1/
LLM_API_KEY=sk-xx
DEFAULT_LLM_MODEL_NAME=gpt-3.5-turbo
```

### Start

```bash
myla
```

or

```bash
python -m myla
```

For more startup options:
```bash
myla --help
```

### WebUI

Myla provides a simple web interface that makes it easy to develop and debug assistants.

Access from your browser: http://localhost:2000/

![Screenshot](webui/static/images/screenshot.png)

### API

You can directly use the OpenAI python SDK to access the assistants API.

* API Docs: http://localhost:2000/api/docs
* Swagger: http://localhost:2000/api/swagger


## Community

Myla is still under rapid development, and community contributions are welcome.