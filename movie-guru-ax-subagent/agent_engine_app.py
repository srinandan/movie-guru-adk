import json
import logging
import datetime
from typing import Any

import vertexai
from google.adk.artifacts import GcsArtifactService

import google.auth

from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp, A2aAgent, A2aAgent
from agent_config import agent_card
from agent_executor import ConversationAnalysisAgentExecutor


def deploy_agent_engine_app(
    project: str,
    location: str,
    agent_name: str | None = None,
    requirements_file: str = ".requirements.txt",
    extra_packages: list[str] = ["agent_executor.py", "prompt.py", "agent_config.py", "__main__.py"],
    env_vars: dict[str, Any] = {},
) -> agent_engines.AgentEngine:
    """Deploy the agent engine app to Vertex AI."""

    staging_bucket_uri = f"gs://{project}"
    artifacts_bucket_name = f"{project}"

    vertexai.init(project=project,
                  location=location,
                  staging_bucket=staging_bucket_uri)
    
    a2a_agent = A2aAgent(
        agent_card=agent_card, 
        agent_executor_builder=ConversationAnalysisAgentExecutor
    )

    a2a_agent.set_up()

    # Read requirements
    with open(requirements_file) as f:
        requirements = f.read().strip().split("\n")

    agent_engine = AdkApp(
        agent=a2a_agent,
        artifact_service_builder=lambda: GcsArtifactService(
            bucket_name=artifacts_bucket_name),
    )

    # Set worker parallelism to 1
    env_vars["NUM_WORKERS"] = "1"

    # Common configuration for both create and update operations
    agent_config = {
        "agent_engine": agent_engine,
        "display_name": agent_name,
        "description": "A Movie Recommendation AI Agent",
        "extra_packages": extra_packages,
        "env_vars": env_vars,
    }
    logging.info(f"Agent config: {agent_config}")
    agent_config["requirements"] = requirements

    # Check if an agent with this name already exists
    existing_agents = list(
        agent_engines.list(filter=f"display_name={agent_name}"))
    if existing_agents:
        # Update the existing agent with new configuration
        logging.info(f"Updating existing agent: {agent_name}")
        remote_agent = existing_agents[0].update(**agent_config)
    else:
        # Create a new agent if none exists
        logging.info(f"Creating new agent: {agent_name}")
        remote_agent = agent_engines.create(**agent_config)

    config = {
        "remote_agent_engine_id": remote_agent.resource_name,
        "deployment_timestamp": datetime.datetime.now().isoformat(),
    }
    config_file = "deployment_metadata.json"

    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    logging.info(f"Agent Engine ID written to {config_file}")

    return remote_agent


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Deploy agent engine app to Vertex AI")
    parser.add_argument(
        "--project",
        default=None,
        help="GCP project ID (defaults to application default credentials)",
    )
    parser.add_argument(
        "--location",
        default="us-central1",
        help="GCP region (defaults to us-central1)",
    )
    parser.add_argument(
        "--agent-name",
        default="conversation-analysis-agent",
        help="Name for the agent engine",
    )
    parser.add_argument(
        "--requirements-file",
        default=".requirements.txt",
        help="Path to requirements.txt file",
    )
    parser.add_argument(
        "--extra-packages",
        nargs="+",
        default=["."],
        help="Additional packages to include",
    )
    parser.add_argument(
        "--set-env-vars",
        help=
        "Comma-separated list of environment variables in KEY=VALUE format",
    )
    args = parser.parse_args()

    # Parse environment variables if provided

    # initialize with the database password
    env_vars = {
        "DB_PASSWORD": {
            "secret": "postgres-root-password-secret",
            "version": "1"
        },
    }

    if args.set_env_vars:
        for pair in args.set_env_vars.split(","):
            key, value = pair.split("=", 1)
            env_vars[key] = value

    if not args.project:
        _, args.project = google.auth.default()

    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🤖 DEPLOYING AGENT TO VERTEX AI AGENT ENGINE 🤖         ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    deploy_agent_engine_app(
        project=args.project,
        location=args.location,
        agent_name=args.agent_name,
        requirements_file=args.requirements_file,
        extra_packages=args.extra_packages,
        env_vars=env_vars,
    )
