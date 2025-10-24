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
from typing import Optional, Dict, Any

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
from app.utils.model_armor import sanitize_user_prompt
from app.subagents.recommendmovies.prompt import AGENT_INSTRUCTION

# output schema cannot be used with tools


def get_mcp_url() -> str:
    """Returns the MCP URL."""
    return f"https://{MCPTOOLSET}/sse"

def before_model_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Inspects the latest user message for improper requests. If found, blocks the LLM call
    and returns a predefined LlmResponse. Otherwise, returns None to proceed.
    """
    agent_name = callback_context.agent_name # Get the name of the agent whose model call is being intercepted
    print(f"--- Callback: before_model_callback running for agent: {agent_name} ---")

    # Extract the text from the latest user message in the request history
    last_user_message_text = ""
    if llm_request.contents:
        # Find the most recent message with role 'user'
        for content in reversed(llm_request.contents):
            if content.role == 'user' and content.parts:
                # Assuming text is in the first part for simplicity
                if content.parts[0].text:
                    last_user_message_text = content.parts[0].text
                    break # Found the last user message text

    print(f"--- Callback: Inspecting last user message: '{last_user_message_text[:100]}...' ---") # Log first 100 chars

    # --- Guardrail Logic ---
    sanitized_response = sanitize_user_prompt(last_user_message_text)
    if sanitized_response is not None:
        return LlmResponse(
            content=types.Content(
                role="model", # Mimic a response from the agent's perspective
                parts=[types.Part(text="I cannot process this request because it movie-guru-agent policies")],
            )
        )
    else:
        # improper request not found, allow the request to proceed to the LLM
        return None # Returning None signals ADK to continue normally

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
                 before_model_callback=before_model_callback,
                 before_tool_callback=get_session_user_id,
                 instruction=AGENT_INSTRUCTION,
                 tools=[
                     AgentTool(agent=user_profile_agent),
                     load_memory,
                     MCPToolset(connection_params=SseConnectionParams(
                            url=mcp_url
                         ),
                         header_provider=lambda ctx: {'x-user-id':user_id_context.get()},
                         errlog=logging)
                 ],
                 output_key="recommenderOutput")
