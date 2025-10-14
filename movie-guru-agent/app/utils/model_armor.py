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

from google.cloud import modelarmor_v1
from google.api_core.exceptions import InternalServerError
from .envvars import PROJECT_ID, MODEL_ARMOR_TEMPLATE


project_id = PROJECT_ID
location = "global"
template_id = MODEL_ARMOR_TEMPLATE

client = modelarmor_v1.ModelArmorClient(transport="rest", client_options={
                                        "api_endpoint": "modelarmor.googleapis.com"})


def sanitize_model_response(model_response_text: str) -> str | None:
    model_response_data = modelarmor_v1.DataItem()
    model_response_data.text = str(model_response_text)

    request = modelarmor_v1.SanitizeModelResponseRequest(
        name=f"projects/{project_id}/locations/{location}/templates/{template_id}",
        model_response_data=model_response_data,
    )
    try:
        response = client.sanitize_model_response(
            request=request
        )
        if response.sanitization_result.filter_match_state == "MATCH_FOUND":
            return "The model's response has been flagged to violate policies of movie-guru"
    except InternalServerError as e:
        print(f"internal server error {e}")

    return None


def sanitize_user_prompt(user_message: str) -> str | None:
    user_prompt_data = modelarmor_v1.DataItem()
    user_prompt_data.text = str(user_message)
    request = modelarmor_v1.SanitizeUserPromptRequest(
        name=f"projects/{project_id}/locations/{location}/templates/{template_id}",
        user_prompt_data=user_prompt_data,
    )
    try:
        response = client.sanitize_user_prompt(
            request=request
        )
        if response.sanitization_result.filter_match_state == "MATCH_FOUND":
            return "The user's prompt has been flagged to violate policies of movie-guru"
    except InternalServerError as e:
        print(f"internal server error {e}")

    return None
