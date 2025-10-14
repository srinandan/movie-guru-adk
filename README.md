# Movie Guru ADK

This repository contains the source code for the Movie Guru, an AI-powered movie recommendation chatbot written in ADK.

The project is structured as a monorepo containing three main components: a chatbot frontend, a backend agent, and a supporting tools service.

## Architecture

The application is composed of the following core components:

*   **`movie-chatbot/`**: A web-based frontend built with Vue.js that provides the user interface for interacting with the chatbot.
*   **`movie-guru-agent/`**: The core backend agent responsible for processing user messages, understanding intent, and providing movie recommendations. It is built in Python and designed as a multi-agent system with sub-agents for conversation analysis, movie recommendations, and user profile management.
*   **`movie-guru-tools/`**: A set of supporting tools and services, also built in Python, that likely provide APIs or utilities consumed by the main agent.

## Technology Stack

*   **Frontend**: Vue.js, Vite
*   **Backend**: Python
*   **Infrastructure & Deployment**: Google Cloud Platform (GCP), Docker, Terraform, Cloud Deploy

## Repository Structure

```
.
├── movie-chatbot/      # Vue.js frontend for the chatbot UI
├── movie-guru-agent/   # Core Python backend agent and sub-agents
│   ├── app/            # Main application logic
│   ├── deployment/     # GCP deployment scripts (Terraform, Cloud Deploy)
│   └── ...
└── movie-guru-tools/   # Supporting Python services
    ├── app/            # Main application logic
    └── deployment/     # GCP deployment scripts
```

## Getting Started

To get the full application running, you will need to set up each component individually. Please refer to the `README.md` file within each component's directory for specific setup and development instructions.

*   [movie-chatbot/README.md](./movie-chatbot/README.md)
*   [movie-guru-agent/README.md](./movie-guru-agent/README.md)
*   [movie-guru-tools/README.md](./movie-guru-tools/README.md)

## Deployment

The application is designed to be deployed on Google Cloud Platform. The `movie-guru-agent/deployment` directory contains Terraform scripts for provisioning the necessary infrastructure (e.g., Cloud Run, GCS, Artifact Registry) and Cloud Deploy YAML files for orchestrating deployments.

## Contributing

Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for details on how to contribute to this project.

## License

This project is licensed under the terms of the [LICENSE.txt](./LICENSE.txt) file.
