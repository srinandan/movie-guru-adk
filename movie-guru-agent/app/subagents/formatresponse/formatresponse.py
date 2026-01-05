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
from google.genai import types
from app.utils.model import get_model
from pydantic import BaseModel, Field
from typing import List


class RecommendationOutput(BaseModel):
    name: str = Field(default=None, description="The name of the movie")
    released: int = Field(default=None, description="The year of release of the movie")
    plot: str = Field(default=None, description="The plot of the movie")
    rating: float = Field(default=None, description="The rating of the movie")
    poster: str = Field(default=None, description="The poster of the movie")


class RecommendationsOutput(BaseModel):
    movies: List[RecommendationOutput] = Field(
        default=None, description="An array of recommendations"
    )


def get_formatresponse_agent() -> Agent:
    """Creates and returns the format response agent."""
    return Agent(
        name="formatresponse_agent",
        description="Agent to format the response.",
        instruction="Format the response as per the schema in output schema.",
        model=get_model(),
        output_schema=RecommendationsOutput,
        output_key="formatresponseOutput",
    )
