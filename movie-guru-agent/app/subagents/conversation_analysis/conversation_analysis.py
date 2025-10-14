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
from pydantic import BaseModel, Field
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from google.genai import types
from typing import Optional
from app.utils.model import get_model
from app.utils.model_armor import sanitize_model_response, sanitize_user_prompt
from app.utils.logging import logger


class ConversationOutput(BaseModel):
    outcome: str = Field(
        description="Classification of the conversation outcome")
    sentiment: str = Field(description="Classification of the user sentiment")
    reasoning: str = Field(
        description="Reasoning for the classification of outcome and sentiment"
    )


def after_model_callback(callback_context,
                         llm_response) -> Optional[LlmResponse | None]:
    print("after_model_callback - conversation_analysis_agent")
    model_response_text = llm_response.content.parts[0].text
    sanitized_response = sanitize_model_response(str(model_response_text))
    if sanitized_response is not None:
        return LlmResponse(content=types.Content(
            role="model",
            parts=[types.Part(text=sanitized_response)],
        ),
                           grounding_metadata=llm_response.grounding_metadata)


def before_model_callback(
        callback_context: CallbackContext,
        llm_request: LlmRequest) -> Optional[LlmResponse | None]:
    user_message = ""
    if llm_request.contents and llm_request.contents[-1].role == 'user':
        if llm_request.contents[-1].parts:
            user_message = llm_request.contents[-1].parts[0].text
            sanitized_response = sanitize_user_prompt(str(user_message))
            if sanitized_response is not None:
                return LlmResponse(content=types.Content(
                    role="model",
                    parts=[types.Part(text=sanitized_response)],
                ))
        else:
            return None
    else:
        return None


def get_conversation_analysis_agent() -> Agent:
    """Creates and returns the conversation analysis agent."""
    return Agent(
        name="conversation_analysis_agent",
        model=get_model(),
        description=
        "Agent to analyze the conversation between the user and other agents",
        instruction="""
                You are an AI assistant designed to analyze conversations between users and a movie expert agent.
                Your task is to objectively assess the flow of the conversation and determine the outcome of the agent's response based solely on the user's reaction to it.
                You also need to determine the user's sentiment based on their last message (it can be positive, negative, neutral, or ambiguous).
                You only get a truncated version of the conversation history.

                Here's how to analyze the conversation:

                1. Read the conversation history carefully, paying attention to the sequence of messages and the topics discussed.
                2. Focus on the agent's response and how the user reacts to it.

                Guidelines for classification of the conversation outcome:

                *   OUTCOMEIRRELEVANT: The agent's response is not connected to the user's previous turn or doesn't address the user's query or request.
                *   OUTCOMEACKNOWLEDGED: The user acknowledges the agent's response with neutral remarks like "Okay," "Got it," or a simple "Thanks" without indicating further interest or engagement.
                *   OUTCOMEREJECTED: The user responds negatively to the agent's response like "No," "I don't like it," or a simple "No thanks" without indicating further interest or engagement.
                *   OUTCOMEENGAGED: The user shows interest in the agent's response and wants to delve deeper into the topic. This could be through follow-up questions, requests for more details, or expressing a desire to learn more about the movie or topic mentioned by the agent.
                *   OUTCOMETOPICCHANGE: The user shifts the conversation to a new topic unrelated to the agent's response.
                *   OUTCOMEAMBIGUOUS: The user's response is too vague or open-ended to determine the outcome with certainty.

                Examples:

                User: "I'm looking for a movie with strong female characters."
                Agent: "Have you seen 'Alien'?"
                User: "Tell me more about it."
                Outcome: OUTCOMEENGAGED (The user shows interest in the agent's suggestion and wants to learn more.)

                Agent: "Let me tell you about the movie 'Alien'?"
                User: "I hate that film"
                Outcome: OUTCOMEREJECTED (The user rejects the agent's suggestion.)

                Agent: "Have you seen 'Alien'?"
                User: "No. Tell me about 'Princess diaries'"
                Outcome: OUTCOMETOPICCHANGE (The user shows no interest in the agent's suggestion and changes the topic.)

                Agent: "Have you seen 'Alien'?"
                User: "I told you I am not interested in sci-fi."
                Outcome: OUTCOMEIRRELEVANT (The agent made a wrong suggestion.)

                Guidelines for classification of the user sentiment:
                * SENTIMENTPOSITIVE: If the user expresses excitement, joy etc. Simply rejecting an agent's suggestion is not negative.
                * SENTIMENTNEGATIVE: If the user expresses frustration, irritation, anger etc. Simply rejecting an agent's suggestion is not negative.
                * SENTIMENTNEUTRAL: If the user expresses no specific emotion

                Remember:

                *   Do not make assumptions about the user's satisfaction or perception of helpfulness.
                *   Do not return this response to the user. This is meant for internal analysis only. The user need not know about the outcome.
                *   Focus only on the objective flow of the conversation and how the user's response relates to the agent's previous turn.
                *   If the outcome is unclear based on the user's response, use OutcomeAmbiguous.
    """,
        output_schema=ConversationOutput,
        output_key="conversationAnalysisOutput",
        before_model_callback=before_model_callback,
        after_model_callback=after_model_callback)
