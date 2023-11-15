[English](README.md) | [简体中文](README_zh_CN.md)

# Myla: Deploy an AI assistant compatible with OpenAI locally

Myla stands for MY Local Assistant and is designed and optimized for deploying AI assistants based on large language models (LLMs) in a private environment. Myla provides an API compatible with the OpenAI assistant API, with support for multiple LLM backends. Whether on a laptop or a production server, you can quickly develop and run an AI assistant.

## Quick Start
### Installation

Myla can be installed from PyPI using ·pip·. It is recommended to create a new virtual environment before installation to avoid conflicts.

Python version requirement: <= 3.11

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

For more startup options:
```bash
myla --help
```

### WebUI
Access from your browser: http://localhost:2000/

### API

* API Docs: http://localhost:2000/api/docs
* Swagger: http://localhost:2000/api/swagger


## Community

Myla is still under rapid development, and community contributions are welcome.