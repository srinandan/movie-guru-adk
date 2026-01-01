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

import logging
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import load_memory  # Tool to query memory
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool

from google.genai import types
from app.utils.model import get_model
from app.utils.context import user_id_context
from app.utils.envvars import MCPTOOLSET

from app.subagents.userprofile.userprofile import get_user_profile_agent
from app.subagents.recommendmovies.prompt import AGENT_INSTRUCTION

logging.getLogger("google_adk.google.adk.tools.base_authenticated_tool").setLevel(logging.ERROR)

class RecommendationInput(BaseModel):
    user: str = Field(default=None, 
        description="The user")
    query_text: str = Field(default=None, 
        description="The query")

def get_mcp_url() -> str:
    """Returns the MCP URL."""
    return f"https://{MCPTOOLSET}/sse"

def get_session_user_id(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """Inspects/modifies tool args or skips the tool call."""
    print(f"--- Callback: get_session_user_id running for agent: {tool.name}, tool: {tool_context.agent_name} ---")
    print(f"Session user id: {user_id_context.get()}")
    return None

def get_recommender_agent() -> Agent:
    """Creates and returns the recommender agent."""

    mcp_url = get_mcp_url()

    print(f"MCP URL: {mcp_url}")

    user_profile_agent = get_user_profile_agent()

    return Agent(name="recommender_agent",
                 model=get_model(),
                 description=
                 "Agent to recommend movies based on the user's preferences.",
                 before_tool_callback=get_session_user_id,
                 instruction=AGENT_INSTRUCTION,
                 tools=[
                     AgentTool(agent=user_profile_agent),
                     load_memory,
                     MCPToolset(connection_params=SseConnectionParams(
                            url=mcp_url
                         ),
                         header_provider=lambda ctx: {'x-user-id':user_id_context.get()},
                         errlog=logging),
                 ],
                 output_key="recommenderOutput")
