# Movie Guru Tools MCP Server

Movie Guru Tools is a Model Context Protocol (MCP) server that provides a set of tools for a movie recommendation assistant. It leverages Google Cloud services and a PostgreSQL database with `pgvector` to offer intelligent movie search and user preference management.

## Features

- **Vector Search**: Search for movies using semantic similarity via Vertex AI text embeddings.
- **User Preferences**: Retrieve and update user-specific movie preferences (likes/dislikes for actors, directors, genres, etc.).
- **Recommendations**: Access historical recommendations made to users.
- **Random Discovery**: Get a selection of random movies to inspire users.
- **Cloud Integration**: 
    - **Vertex AI**: Generates high-quality embeddings for movie search.
    - **Cloud Storage**: Serves movie posters via secure, signed URLs.
    - **Cloud Trace**: Implements OpenTelemetry for distributed tracing of tool executions.
    - **Cloud SQL**: Stores movie data and user preferences in a PostgreSQL database with vector support.

## Prerequisites

- Python 3.11 - 3.14
- [uv](https://github.com/astral-sh/uv) for dependency management
- A Google Cloud Project with the following APIs enabled:
    - Vertex AI API
    - Cloud Storage API
    - Cloud Trace API
- A PostgreSQL database with the `pgvector` extension installed.

## Environment Variables

The server requires the following environment variables to be set:

| Variable | Description |
| --- | --- |
| `GOOGLE_CLOUD_PROJECT` | Your Google Cloud Project ID |
| `GOOGLE_CLOUD_LOCATION` | The region for Vertex AI (e.g., `us-central1`) |
| `DB_HOST` | Hostname of the PostgreSQL database |
| `DB_PASSWORD` | Password for the database user |
| `BUCKET_NAME` | (Optional) GCS bucket for movie posters (defaults to `{PROJECT_ID}_posters`) |
| `MODEL_NAME` | (Optional) Vertex AI embedding model (defaults to `text-embedding-004`) |

## Getting Started

### Installation

1. Clone the repository and navigate to the project directory.
2. Install dependencies and set up the environment:

```bash
make install
```

### Running the Server

To run the server locally with auto-reload:

```bash
make local-backend
```

By default, the server runs with the **SSE** (Server-Sent Events) transport on `http://0.0.0.0:8080`.

## Development

### Linting

Run the linting and formatting checks:

```bash
make lint
```

## Deployment

### Google Cloud Run

The project uses Google Cloud Build for deployment. To deploy the server to Cloud Run:

```bash
make backend
```

This command triggers a build and deploy process using `deployment/cd/dev-cloudrun.yaml`.

### Docker

Alternatively, you can build and push the Docker image manually:

```bash
make docker
```

## Project Structure

- `app/`:
    - `server.py`: The main entry point containing tool definitions and server logic.
    - `__init__.py`: Package initialization.
- `deployment/`: Configuration files for CI/CD and cloud deployment (Cloud Run, Cloud Build).
- `pyproject.toml`, `uv.lock`, `uv.toml`: Python project configuration and dependency lock files managed by `uv`.
- `Dockerfile`: Container image definition.
- `Makefile`: Automation for installation, linting, building, and deployment.
- `README.md`: Project documentation.
