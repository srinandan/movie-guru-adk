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

from google.adk.agents import SequentialAgent
from app.subagents.recommendmovies.recommendmovies import get_recommender_agent
from app.subagents.conversation_analysis.conversation_analysis import (
    get_conversation_analysis_agent,
)
from app.subagents.formatresponse.formatresponse import get_formatresponse_agent


def get_agent() -> SequentialAgent:
    """Creates and returns the movie guru agent."""
    return SequentialAgent(
        name="movie_guru_agent",
        sub_agents=[
            get_conversation_analysis_agent(),
            get_recommender_agent(),
            #            get_formatresponse_agent(),
        ],
        description="Executes a sequence of movie conversation analysis, movie recommendations and formatting the response.",
    )


root_agent = get_agent()
