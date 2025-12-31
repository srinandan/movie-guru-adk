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
import google.auth
from google.cloud import resourcemanager_v3

DB_NAME = "fake-movies-db"

DB_PASSWORD = os.environ.setdefault("DB_PASSWORD", "changeit")
DB_HOST = os.environ.setdefault("DB_HOST", "localhost")

_, project_id = google.auth.default()
PROJECT_ID = os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)

REGION = os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
VERTEX_AI = os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
USER = os.environ.setdefault("USER_ID", "fake")
MODEL = os.environ.setdefault("MODEL_NAME", "openai/gemini-2.0-flash-lite")
MODEL_ARMOR_TEMPLATE = os.environ.setdefault("MODEL_ARMOR_TEMPLATE",
                                             "movie-guru")
POSTER_DIRECTORY = os.environ.setdefault("POSTER_DIRECTORY", "/mnt")

A2A_CONV_AGENT = os.environ.setdefault("A2A_CONV_AGENT", "localhost:8083")

os.environ['GOOGLE_CLOUD_QUOTA_PROJECT']=f"{PROJECT_ID}"
os.environ['OTEL_RESOURCE_ATTRIBUTES'] = f"gcp.project_id={PROJECT_ID}"
os.environ['OTEL_SERVICE_NAME']="movie-guru-agent"
os.environ['OTEL_TRACES_EXPORTER']="otlp"
os.environ['OTEL_SPAN_ATTRIBUTE_VALUE_LENGTH_LIMIT']="512"
os.environ['OTEL_EXPORTER_OTLP_ENDPOINT']="https://telemetry.googleapis.com"
os.environ['OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED']="true"
os.environ['OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT']="true"

def get_gcp_project_number() -> str | None:
    """
    Retrieves the GCP Project Number given a Project ID.

    Args:
        project_id (str): The Google Cloud Project ID (e.g., "my-project-123").

    Returns:
        str or None: The Project Number as a string, or None if the project
                     is not found or an error occurs.
    """
    try:
        client = resourcemanager_v3.ProjectsClient()
        request = resourcemanager_v3.GetProjectRequest(
            name=f"projects/{PROJECT_ID}")
        project = client.get_project(request=request)

        # The project number is part of the 'name' attribute in the format "projects/PROJECT_NUMBER"
        project_number = project.name.split('/')[-1]
        return project_number
    except Exception as e:
        print(f"Error getting project number for ID '{PROJECT_ID}': {e}")
        return None


PROJECT_NUMBER = get_gcp_project_number()
MCPTOOLSET = os.environ.setdefault(
    "MCPTOOLSET_URL",
    f"movie-guru-mcp-server-{PROJECT_NUMBER}.{REGION}.run.app")

API_BASE = os.environ.setdefault("OPENAI_API_BASE", 
    f"https://litellm-server-{PROJECT_NUMBER}.{REGION}.run.app/v1")

os.environ.setdefault("OPENAI_API_KEY", "")
# API_BASE = os.environ.setdefault("OPENAI_API_BASE", "http://localhost:4000/v1")