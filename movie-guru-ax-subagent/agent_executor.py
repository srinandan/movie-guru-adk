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

# agent_executor.py
import logging
import os

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from a2a.server.tasks import TaskUpdater
from a2a.types import TaskState, TextPart, UnsupportedOperationError
from a2a.utils.errors import ServerError
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService
from google.adk.agents import LlmAgent
from google.adk import Runner
from pydantic import BaseModel, Field
from google.genai import types

logger = logging.getLogger(__name__)

# Conversation schema
class ConversationOutput(BaseModel):
    outcome: str = Field(
        description="Classification of the conversation outcome")
    sentiment: str = Field(default=None, description="Classification of the user sentiment")
    reasoning: str = Field(default=None,
        description="Reasoning for the classification of outcome and sentiment"
    )

class ConversationAnalysisAgentExecutor(AgentExecutor):
    """Agent executor that uses the ADK to analyze conversations."""

    def __init__(self):
        self.agent = None
        self.runner = None

    def _init_agent(self):
        self.agent = LlmAgent(
            model='gemini-2.5-flash',
            name="conversation_analysis_agent",
            description=
            "Agent to analyze the conversation between the user and agent",
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
            output_key="conversationAnalysisOutput"    
        )
        self.runner = self.runner = Runner(
            app_name=self.agent.name,
            agent=self.agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        raise ServerError(error=UnsupportedOperationError())
    
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        if self.agent is None:
            self._init_agent()
        logger.debug(f'Executing agent {self.agent.name}')

        query = context.get_user_input()

        updater = TaskUpdater(event_queue, context.task_id, context.context_id)

        if not context.current_task:
            await updater.submit()

        await updater.start_work()

        content = types.Content(role='user', parts=[types.Part(text=query)])
        session = await self.runner.session_service.get_session(
            app_name=self.runner.app_name,
            user_id='123',
            session_id=context.context_id,
        ) or await self.runner.session_service.create_session(
            app_name=self.runner.app_name,
            user_id='123',
            session_id=context.context_id,
        )

        async for event in self.runner.run_async(
            session_id=session.id, user_id='123', new_message=content
        ):
            logger.debug(f'Event from ADK {event}')
            if event.is_final_response():
                parts = event.content.parts
                text_parts = [
                    TextPart(text=part.text) for part in parts if part.text
                ]
                await updater.add_artifact(
                    text_parts,
                    name='result',
                )
                await updater.complete()
                break
            await updater.update_status(
                TaskState.working, message=new_agent_text_message('Working...')
            )
        else:
            logger.debug('Agent failed to complete')
            await updater.update_status(
                TaskState.failed,
                message=new_agent_text_message(
                    'Failed to generate a response.'
                ),
            )    