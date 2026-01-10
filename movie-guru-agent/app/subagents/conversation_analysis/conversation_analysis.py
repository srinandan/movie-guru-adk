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

import httpx
from app.utils.context import user_id_context
from a2a.client import ClientConfig, ClientFactory
from a2a.types import TransportProtocol
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from app.utils.envvars import A2A_CONV_AGENT

factory = ClientFactory(
    ClientConfig(
        httpx_client=httpx.AsyncClient(
            headers={
                "x-user-id": user_id_context.get(), 
            }
        ),
    )
)

def get_conversation_analysis_agent() -> RemoteA2aAgent:
    """Creates and returns the conversation analysis agent."""
    return RemoteA2aAgent(
        name="conversation_analysis_agent_test",
        description=(
            "Agent to analyze a conversation where the user is asking for movie recommendations"
        ),
        agent_card=f"https://{A2A_CONV_AGENT}{AGENT_CARD_WELL_KNOWN_PATH}",
        a2a_client_factory=factory,
    )
