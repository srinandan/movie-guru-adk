# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from a2a.types import AgentCapabilities, AgentCard, AgentSkill, TransportProtocol
from google.cloud import resourcemanager_v3


def get_gcp_project_number(project_id: str) -> str | None:
    """Retrieves the GCP Project Number given a Project ID."""
    try:
        client = resourcemanager_v3.ProjectsClient()
        request = resourcemanager_v3.GetProjectRequest(name=f"projects/{project_id}")
        project = client.get_project(request=request)
        return project.name.split("/")[-1]
    except Exception as e:
        print(f"Error getting project number for ID '{project_id}': {e}")
        return None


PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
REGION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
PROJECT_NUMBER = get_gcp_project_number(PROJECT_ID)

skill = AgentSkill(
    id="get_analysis",
    name="Get Conversation Analysis",
    description="Analyze the conversation between the user and agent.",
    tags=["Sentiment", "Analysis", "Movies"],
    examples=[
        "I am looking for a movie with strong female characters.",
        "I told you I am not interested in sci-fi",
    ],
)

capabilities = AgentCapabilities(streaming=False)

agent_card = AgentCard(
    name="Conversation Analysis Agent",
    description="Agent to analyze the conversation between the user and agent",
    url="http://localhost:9999/",
    version="1.0.0",
    default_input_modes=["text"],
    default_output_modes=["application/json"],
    skills=[skill],
    preferred_transport=TransportProtocol.http_json,
    capabilities=capabilities,
    supports_authenticated_extended_card=True,
)
