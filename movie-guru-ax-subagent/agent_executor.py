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
from prompt import AGENT_INSTRUCTION

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
            instruction=AGENT_INSTRUCTION,
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