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

from google.adk.agents.llm_agent import Agent
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

remote_agent = RemoteA2aAgent(
    name="conversation_analysis_agent_test",
    description=(
        "Agent to analyze a conversation where the user is asking for movie recommendations"
    ),
    agent_card=f"http://localhost:8080/{AGENT_CARD_WELL_KNOWN_PATH}",
)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="root_agent",
    instruction="""
      You are a helpful assistant that is used in the test Google A2A. Call the remote_agent
      and return the information.
    """,
    global_instruction=(
        "You are orchestration agent, call the remote agent and return the information."
    ),
    sub_agents=[remote_agent],
)
