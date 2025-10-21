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

from google.adk.agents import Agent
from google.adk.models import LlmResponse, LlmRequest
from google.genai import types
from typing import Optional
from pydantic import BaseModel, Field
from app.utils.model import get_model
from app.utils.logging import logger
from app.subagents.userprofile.prompt import AGENT_INSTRUCTION


class UserProfileOutput(BaseModel):
    justification: str = Field(default=None, 
        description="The reason about the query was created this way")
    safetyIssue: bool = Field(default=None, 
        description="True if the query is considered dangerous")
    profileChangeRecommendations: list = Field(default=None, 
        description="A list of profile change recommendations")


def after_model_callback(callback_context,
                         llm_response) -> Optional[LlmResponse | None]:
    print("after_model_callback - user_profile_agent")
    return None


def get_user_profile_agent() -> Agent:
    """Creates and returns the user profile agent."""
    return Agent(name="user_profile_agent",
                 model=get_model(),
                 description="Agent to profile the user's likes and dislikes.",
                 instruction=AGENT_INSTRUCTION,
                 output_schema=UserProfileOutput,
                 output_key="userProfileOutput",
                 after_model_callback=after_model_callback)
