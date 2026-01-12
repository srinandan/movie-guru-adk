# movie-guru-ax-subagent

This agent analyzes a conversation between the agent and the user and publishes a custom metric to Cloud monitoring.

## Project Structure

This project is organized as follows:

```
movie-guru-ax-subagent/
├── app/                 # Core application code
│   ├── agent.py         # Main agent logic
│   ├── agent_engine_app.py # Agent Engine application logic
│   └── app_utils/       # App utilities and helpers
├── .cloudbuild/         # CI/CD pipeline configurations for Google Cloud Build
├── deployment/          # Infrastructure and deployment scripts
├── notebooks/           # Jupyter notebooks for prototyping and evaluation
├── tests/               # Unit, integration, and load tests
├── Makefile             # Makefile for common commands
├── GEMINI.md            # AI-assisted development guide
└── pyproject.toml       # Project dependencies and configuration
```

> 💡 **Tip:** Use [Gemini CLI](https://github.com/google-gemini/gemini-cli) for AI-assisted development - project context is pre-configured in `GEMINI.md`.

## Requirements

Before you begin, ensure you have:
- **uv**: Python package manager (used for all dependency management in this project) - [Install](https://docs.astral.sh/uv/getting-started/installation/) ([add packages](https://docs.astral.sh/uv/concepts/dependencies/) with `uv add <package>`)
- **Google Cloud SDK**: For GCP services - [Install](https://cloud.google.com/sdk/docs/install)
- **Terraform**: For infrastructure deployment - [Install](https://developer.hashicorp.com/terraform/downloads)
- **make**: Build automation tool - [Install](https://www.gnu.org/software/make/) (pre-installed on most Unix-based systems)


## Commands

| Command              | Description                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------- |
| `make install`       | Install all required dependencies using uv                                                  |
| `make playground`    | Launch local development environment for testing agent |
| `make deploy`        | Deploy agent to Agent Engine |
| `make lint`          | Run code quality checks (codespell, ruff, ty)                                               |


### Local Testing

> **Note:** For Agent Engine deployments, local testing with A2A endpoints requires deployment first, as `make playground` uses the ADK web interface. For local development, use `make playground`. To test A2A protocol compliance, follow the Remote Testing instructions below.

### Remote Testing

1. Deploy your agent:
   ```bash
   make deploy
   ```

2. Get an authentication token:
   ```bash
   gcloud auth print-access-token
   ```

3. In the inspector UI at http://localhost:5001:
   - Add an HTTP header with name: `Authorization`
   - Set the value to: `Bearer <your-token-from-step-2>`
   - Connect to your Agent Engine URL using this format:
     ```
     https://us-central1-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{REGION}/reasoningEngines/{ENGINE_ID}/a2a/v1/card
     ```
     Find your `PROJECT_ID`, `REGION`, and `ENGINE_ID` in the `latest_deployment_metadata.json` file created after deployment.

The project includes a `GEMINI.md` file that provides context for AI tools like Gemini CLI when asking questions about your template.
