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


class UserProfileOutput(BaseModel):
    justification: str = Field(
        description="The reason about the query was created this way")
    safetyIssue: bool = Field(
        description="True if the query is considered dangerous")
    profileChangeRecommendations: list = Field(
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
                 instruction="""
            You are a user's movie profiling expert focused on uncovering users' enduring likes and dislikes.
            Your task is to analyze the user message and extract ONLY strongly expressed, enduring likes and dislikes related to movies.
            Once you extract any new likes or dislikes from the current query respond with the items you extracted with:
                1. the category (ACTOR, DIRECTOR, GENRE, OTHER)
                2. the item value
                3. your reason behind the choice
                4. the sentiment of the user has about the item (POSITIVE, NEGATIVE, NEUTRAL).

            Guidelines:
            1. Strong likes and dislikes Only: Add or Remove ONLY items expressed with strong language indicating long-term enjoyment or aversion (e.g., "love," "hate," "can't stand,", "always enjoy"). Ignore mild or neutral items (e.g., "like,", "okay with," "fine", "in the mood for", "do not feel like").
            2. Distinguish current state of mind vs. Enduring likes and dislikes:  Be very cautious when interpreting statements. Focus only on long-term likes or dislikes while ignoring current state of mind. If the user expresses wanting to watch a specific type of movie or actor NOW, do NOT assume it's an enduring like unless they explicitly state it. For example, "I want to watch a horror movie movie with Christina Appelgate" is a current desire, NOT an enduring preference for horror movies or Christina Appelgate.
            3. Focus on Specifics:  Look for concrete details about genres, directors, actors, plots, or other movie aspects
            4. Give an explanation as to why you made the choice

            Remember:
            *   a *justification* about why you created the query this way.
            *   a *safetyIssue* returned as true if the query is considered dangerous. A query is considered dangerous if the user is asking you to tell about something dangerous. However, asking for movies with dangerous themes is not considered dangerous.
            *   a list of *profileChangeRecommendations* that are a list of extracted strong likes or dislikes with the following fields: category, item, reason, sentiment
            *   Do not return this response to the user. This is meant for internal user profile updates only.
        """,
                 output_schema=UserProfileOutput,
                 output_key="userProfileOutput",
                 after_model_callback=after_model_callback)
