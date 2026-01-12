# Movie Guru ADK

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

This repository contains the source code for the Movie Guru, an AI-powered movie recommendation chatbot written in ADK.

The project is structured as a monorepo containing three main components: a chatbot frontend, a backend agent, and a supporting tools service.

## Architecture

The application is composed of the following core components:

![Infra Deployment](./infra.png)

* **`movie-chatbot/`** (Frontend): A web-based frontend built with Vue.js that provides the user interface for interacting with the chatbot.
* **`movie-guru-agent/`** (Orchestration Agent): The core backend agent responsible for processing user messages, understanding intent, and providing movie recommendations. It is built in Python and designed as a multi-agent system with sub-agents for conversation analysis, movie recommendations, and user profile management.
* **`movie-guru-tools/`** (MCP Server): A set of supporting tools and services, also built in Python, that likely provide APIs or utilities consumed by the main agent.
* **`movie-guru-loadgen/`**: A Go-based load generation tool that constantly sends requests to the `movie-guru-agent` server for performance testing.
* **`ollama/`**: Contains deployment configurations for running local models like `gemma3:4b` via Ollama for local development and execution.
* **`movie-guru-ax-subagent/`** (Analysis Agent): An ADK-based A2A sub-agent that analyzes conversation sentiment to generate a customer satisfaction metric.
* **`litellm-proxy/`**: A proxy server for serving models from Vertex AI or self-hosted models.

## Repository Structure

```sh
├── litellm-proxy         # Litellm proxy server
│   └── deployment
├── movie-chatbot         # Vue.js frontend for the chatbot UI
│   ├── deployment
│   └── src
├── movie-guru-agent      # Core Python backend agent and sub-agents
│   ├── app
│   └── deployment
├── movie-guru-ax-subagent # A2A sub-agent for conversation analysis
│   └── deployment
├── movie-guru-loadgen    # Go-based load generation server
├── movie-guru-tools      # MCP Server to access Movies Vector database
│   ├── app
│   └── deployment
├── ollama                # Ollama deployment for local models  
│   └── deployment
├── terraform             # Terraform scripts for provisioning the necessary infrastructure
│   ├── movies-data       # Movies data
│   └── movies-posters    # Movies posters
```

## Getting Started

The application is designed to be deployed on Google Cloud Platform. The [terraform](./terraform/README.md) directory contains Terraform scripts for provisioning the necessary infrastructure (e.g., Cloud SQL, GCS, Artifact Registry). This version uses Cloud Run as the runtime for AI Agents. To see the version that uses Vertex AI, please see this [branch](https://github.com/srinandans/movie-guru-adk/tree/reasoning).

```sh
cd terraform && make worker-pool && make backend
cd movies-data && make backend && cd ..
cd movies-posters && gsutil -m cp -r *.png gs://${PROJECT_ID}_posters && cd ..
```

To get the full application running, you will need to set up each component individually. Please refer to the `README.md` file within each component's directory for specific setup and development instructions.

* [movie-chatbot/README.md](./movie-chatbot/README.md): `cd movie-chatbot && make backend`
* [movie-guru-agent/README.md](./movie-guru-agent/README.md): `cd movie-guru-agent && make backend`
* [movie-guru-tools/README.md](./movie-guru-tools/README.md): `cd movie-guru-tools && make backend`
* [movie-guru-loadgen/README.md](./movie-guru-loadgen/README.md): `cd movie-guru-loadgen && make backend`
* [ollama/README.md](./ollama/README.md): `cd ollama && make backend`
* [movie-guru-ax-subagent/README.md](./movie-guru-ax-subagent/README.md): `cd movie-guru-ax-subagent && make backend`


## Contributing

Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for details on how to contribute to this project.

## Support

This demo is *NOT* endorsed by Google or Google Cloud. The repo is intended for educational/hobbyists use only.

## License

This project is licensed under the terms of the [LICENSE.txt](./LICENSE.txt) file. The AI generated movie data and posters in the repo are licensed under the Creative Commons Attribution 4.0 International License. To view a copy of this license, visit <http://creativecommons.org/licenses/by/4.0/>
