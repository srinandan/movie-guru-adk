# ruff: noqa
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

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps.app import App

import os
import google.auth

from .prompt import AGENT_INSTRUCTION
from .model import get_model
from pydantic import BaseModel, Field

_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
REGION = os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

# Conversation schema
class ConversationOutput(BaseModel):
    outcome: str = Field(description="Classification of the conversation outcome")
    sentiment: str = Field(
        default=None, description="Classification of the user sentiment"
    )
    reasoning: str = Field(
        default=None,
        description="Reasoning for the classification of outcome and sentiment",
    )

root_agent = Agent(
    name="conversation_analysis_agent",
    model=get_model(),
    description="Agent to analyze the conversation between the user and agent",
    instruction=AGENT_INSTRUCTION,
    output_schema=ConversationOutput,
    output_key="conversationAnalysisOutput",
)

app = App(root_agent=root_agent, name="conversation_analysis_agent")
