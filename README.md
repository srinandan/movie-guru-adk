# Movie Guru ADK

This repository contains the source code for the Movie Guru, an AI-powered movie recommendation chatbot written in ADK.

The project is structured as a monorepo containing three main components: a chatbot frontend, a backend agent, and a supporting tools service.

## Architecture

The application is composed of the following core components:

![Infra Deployment](./infra.png)

* **`movie-chatbot/`** (Frontend): A web-based frontend built with Vue.js that provides the user interface for interacting with the chatbot.
* **`movie-guru-agent/`** (Orchestration Agent): The core backend agent responsible for processing user messages, understanding intent, and providing movie recommendations. It is built in Python and designed as a multi-agent system with sub-agents for conversation analysis, movie recommendations, and user profile management.
* **`movie-guru-tools/`** (MCP Server): A set of supporting tools and services, also built in Python, that likely provide APIs or utilities consumed by the main agent.
* **`a2atest/`**: An ADK-based agent-to-agent (A2A) client used to test A2A-enabled agents.
* **`movie-guru-loadgen/`**: A Go-based load generation tool that constantly sends requests to the `movie-guru-agent` server for performance testing.
* **`movie-guru-ax-subagent/`** (Analysis Agent): An ADK-based A2A sub-agent that analyzes conversation sentiment to generate a customer satisfaction metric.


## Repository Structure

```sh
.
├── movie-chatbot/      # Vue.js frontend for the chatbot UI
├── a2atest/            # ADK-based A2A test client
├── movie-guru-agent/   # Core Python backend agent and sub-agents
├── movie-guru-ax-subagent/ # A2A sub-agent for conversation analysis
├── movie-guru-loadgen/ # Go-based load generation server
└── movie-guru-tools/   # Supporting Python services
```

## Getting Started

To get the full application running, you will need to set up each component individually. Please refer to the `README.md` file within each component's directory for specific setup and development instructions.

* [movie-chatbot/README.md](./movie-chatbot/README.md): `cd movie-chatbot && make deploy`
* [movie-guru-agent/README.md](./movie-guru-agent/README.md): `cd movie-guru-agent && make deploy`
* [movie-guru-tools/README.md](./movie-guru-tools/README.md): `cd movie-guru-tools && make deploy`
* [a2atest/README.md](./a2atest/README.md): 
* [movie-guru-ax-subagent/README.md](./movie-guru-ax-subagent/README.md): `cd movie-guru-ax-subagent && make deploy`

## Contributing

Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for details on how to contribute to this project.

## Support

This demo is *NOT* endorsed by Google or Google Cloud. The repo is intended for educational/hobbyists use only.

## License

This project is licensed under the terms of the [LICENSE.txt](./LICENSE.txt) file. The AI generated movie data and posters in the repo are licensed under the Creative Commons Attribution 4.0 International License. To view a copy of this license, visit <http://creativecommons.org/licenses/by/4.0/>