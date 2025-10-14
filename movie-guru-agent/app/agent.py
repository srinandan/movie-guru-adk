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

from google.adk.a2a.utils.agent_to_a2a import to_a2a
from a2a.types import AgentCard

# Define A2A agent card
my_agent_card = AgentCard(
    name="movie_guru_agent",
    url="https://movieguruagent.endpoints.srinandans-next25-demo.cloud.goog",
    description=
    "Executes a sequence of user profile, recommendations and sentiment analysis to return a list of movies.",
    version="1.0.0",
    capabilities={},
    skills=[],
    defaultInputModes=["text/plain"],
    defaultOutputModes=["text/plain"],
    supportsAuthenticatedExtendedCard=False,
)


def get_agent() -> SequentialAgent:
    """Creates and returns the movie guru agent."""
    return SequentialAgent(
        name="movie_guru_agent",
        sub_agents=[
            get_recommender_agent(),
        ],
        description=
        "Executes a sequence of user profile, recommendations and sentiment analysis to return a list of movies.",
    )


root_agent = get_agent()
a2a_app = to_a2a(root_agent, port=8000, agent_card=my_agent_card)
