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

GEMINI25 = "gemini-2.5-flash"
DB_NAME = "fake-movies-db"
GEMINI20 = "gemini-2.0-flash"
OLLAMA = "ollama_chat/gemma2:9b"

DB_PASSWORD = os.environ.setdefault("DB_PASSWORD", "changeit")
DB_HOST = os.environ.setdefault("DB_HOST", "localhost")

_, project_id = google.auth.default()
PROJECT_ID = os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)

REGION = os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
VERTEX_AI = os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
USER = os.environ.setdefault("USER_ID", "fake")
MODEL = os.environ.setdefault("MODEL", GEMINI25)
API_BASE = os.environ.setdefault("API_BASE", "http://localhost:11434")
MODEL_ARMOR_TEMPLATE = os.environ.setdefault("MODEL_ARMOR_TEMPLATE",
                                             "movie-guru")
POSTER_DIRECTORY = os.environ.setdefault("POSTER_DIRECTORY", "/mnt")


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
    f"MCPTOOLSET_URL",
    "movie-guru-mcp-server-{PROJECT_NUMBER}.{REGION}.run.app")
