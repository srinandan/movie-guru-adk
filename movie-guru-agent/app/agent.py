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

from google.adk.agents import SequentialAgent
from google.adk.apps.app import App
from google.adk.models import Gemini
from google.genai import types

import os
import google.auth

from app.subagents.recommendmovies.recommendmovies import get_recommender_agent
from app.subagents.conversation_analysis.conversation_analysis import get_conversation_analysis_agent

_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
REGION = os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"


root_agent = SequentialAgent(
        name="movie_guru_agent",
        sub_agents=[
            get_conversation_analysis_agent(),
            get_recommender_agent(),
        ],
        description="Executes a sequence of user profile, recommendations and sentiment analysis to return a list of movies.",
    )

app = App(root_agent=root_agent, name="movie_guru_agent")
