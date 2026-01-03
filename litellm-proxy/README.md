# LiteLLM Proxy - Movie Guru ADK

This directory contains the LiteLLM Proxy configuration and deployment scripts for the Movie Guru project. It provides a unified OpenAI-compatible API interface for multiple LLMs, including Google Vertex AI (Gemini) and Ollama.

## Features

- **Multi-Model Support**: Unified interface for Gemini 2.5 Flash, Gemini 2.0 Flash Lite, text-embedding-004, and local Ollama models.
- **Vertex AI Integration**: Seamless connection to Google Cloud's Vertex AI models.
- **OpenTelemetry (OTEL) Support**: Built-in instrumentation for tracing and monitoring, configured for Google Cloud Telemetry.
- **Guardrails**: Integrated with Google Cloud Model Armor for safety and content filtering.
- **Caching**: Supports Redis for prompt and result caching (configured for production).
- **Deployment Ready**: Includes Dockerfile and Cloud Build configuration for Google Cloud Run.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Google Cloud SDK (gcloud)](https://cloud.google.com/sdk/docs/install)
- `make` utility
- An active Google Cloud Project with Vertex AI API enabled.

## Local Development

To run the LiteLLM Proxy locally using Docker:

1.  **Set Environment Variables**:
    ```bash
    export GEMINI_API_KEY=xxxx
    export GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project)
    export GOOGLE_CLOUD_LOCATION=us-central1
    ```

2.  **Run with Make**:
    ```bash
    make local
    ```
    This command builds the Docker image and runs a container exposed on port `4000`, using `local_config.yaml`.

3.  **Test the Proxy**:
    ```bash
    curl --location 'http://localhost:4000/chat/completions' \
    --header 'Content-Type: application/json' \
    --data '{ \
      "model": "gemini-2.0-flash-lite", \
      "messages": [ \
        { \
          "role": "user", \
          "content": "Hello, how are you?" \
        } \
      ] \
    }'
    ```

## Deployment Details

The Cloud Run deployment (`deployment/cd/dev-cloudrun.yaml`) includes the following configurations:

- **Service Account**: Runs as `movie-guru-chat-server-sa`.
- **Secrets**: Retrieves `GEMINI_API_KEY` from Google Cloud Secret Manager (`gemini-api-key:latest`).
- **Networking**:
    - Connected to `movie-guru-network` and `movie-guru-subnet`.
    - Uses a custom worker pool for Cloud Build.
    - Configured for `internal-and-cloud-load-balancing` ingress.
- **Resources**: Configured with 1 vCPU, 1Gi Memory, and CPU Boost enabled.
- **Environment Variables**: Automatically sets `REDIS_HOST`, `REDIS_PORT`, and `OLLAMA_API_BASE` based on project configuration.

## Configuration Files

- `litellm_config.yaml`: The primary configuration used in production/containerized environments. Includes full model list, Redis caching, and Model Armor guardrails.
- `local_config.yaml`: A minimal configuration for local development, typically mounting a subset of models.
- `Dockerfile`: Based on the official LiteLLM image with additional OTEL instrumentation.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Access token or API key for Vertex AI. |
| `GOOGLE_CLOUD_PROJECT` | Your GCP Project ID. |
| `GOOGLE_CLOUD_LOCATION` | GCP region (e.g., `us-central1`). |
| `REDIS_HOST` | Hostname for Redis cache (Production). |
| `REDIS_PORT` | Port for Redis cache (Production). |
| `OLLAMA_API_BASE` | Base URL for local Ollama instance (optional). |
