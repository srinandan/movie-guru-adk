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

from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from app.utils.envvars import A2A_CONV_AGENT


def get_conversation_analysis_agent() -> RemoteA2aAgent:
    """Creates and returns the conversation analysis agent."""
    return RemoteA2aAgent(
        name="conversation_analysis_agent_test",
        description=(
            "Agent to analyze a conversation where the user is asking for movie recommendations"
        ),
        agent_card=f"https://{A2A_CONV_AGENT}/v1/card",
    )
