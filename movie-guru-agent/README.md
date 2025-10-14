# Movie Guru Agent

## Description

Movie Guru is a website that helps users find movies to watch through an RAG powered chatbot. The movies are all fictional and are generated using GenAI.
The goal of this repo is to explore the best practices when building AI powered applications.

## Project Structure

This project is organized as follows:

```
movie-guru-agent/
├── agent_README.md
├── app                             # Core application code
│   ├── agent_engine_app.py         # Agent Engine application logic
│   ├── agent.py                    # Main agent logic
│   ├── __init__.py
│   ├── server.py                   # FastAPI Backend server
│   ├── subagents
│   │   ├── conversation_analysis/  # Agent for conversation analysis
│   │   ├── recommendmovies/        # Agent for movie recommendation
│   │   └── userprofile/            # Agent for user profile management
│   └── utils/                      # Utility functions and classes
├── deployment/
├── Dockerfile
├── Makefile                        # Makefile for common commands
├── ollama/                         # Gemma 2 9b ollama docker image
├── pyproject.toml                  # Project dependencies and configuration
├── README.md
└── uv.lock
```

## Requirements

Before you begin, ensure you have:

- **uv**: Python package manager - [Install](https://docs.astral.sh/uv/getting-started/installation/)
- **Google Cloud SDK**: For GCP services - [Install](https://cloud.google.com/sdk/docs/install)
- **make**: Build automation tool - [Install](https://www.gnu.org/software/make/) (pre-installed on most Unix-based systems)

## Quick Start (Local Testing)

Install required packages and launch the local development environment:

```bash
make install && make playground
```

## Commands

| Command              | Description                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------- |
| `make install`       | Install all required dependencies using uv                                                  |
| `make playground`    | Launch local development environment with backend and frontend - leveraging `adk web` command.|
| `make backend`       | Deploy agent to Cloud Run |
| `make local-backend` | Launch local development server |

For full command options and usage, refer to the [Makefile](Makefile).
