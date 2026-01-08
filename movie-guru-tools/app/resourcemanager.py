# Copyright 2026 Google LLC
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

from google.cloud import resourcemanager_v3

def get_gcp_project_number(projectId: str) -> str | None:
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
        request = resourcemanager_v3.GetProjectRequest(name=f"projects/{projectId}")
        project = client.get_project(request=request)

        # The project number is part of the 'name' attribute in the format "projects/PROJECT_NUMBER"
        project_number = project.name.split("/")[-1]
        return project_number
    except Exception as e:
        print(f"Error getting project number for ID '{projectId}': {e}")
        return None