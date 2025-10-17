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
import os

import click
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import ConversationAnalysisAgentExecutor
from tracing import CloudTraceLoggingSpanExporter
from opentelemetry import trace
from opentelemetry.instrumentation.starlette import StarletteInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider, export
import google.auth


logger = logging.getLogger(__name__)
logging.basicConfig()

_, project_id = google.auth.default()
PROJECT_ID = os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)

REGION = os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
VERTEX_AI = os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


@click.command()
@click.option('--host', 'host', default='localhost')
@click.option('--port', 'port', default=8080)
def main(host: str, port: int):
    """A2A Telemetry Sample GRPC Server."""

    skill = AgentSkill(
            id='get_analysis',
            name='Get Conversation Analysis',
            description='Analyze the conversation between the user and agent.',
            tags=['Sentiment', 'Analysis', 'Movies'],
            examples=[
                'I am looking for a movie with strong female characters.',
                'I told you I am not interested in sci-fi',
            ],
        )

    agent_executor = ConversationAnalysisAgentExecutor()
    agent_card = AgentCard(
        name='Conversation Analysis Agent',
        description='Agent to analyze the conversation between the user and agent',
        url=f'http://{host}:{port}/',
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )
    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor, task_store=InMemoryTaskStore()
    )


    # Define the service name
    resource = Resource(attributes={SERVICE_NAME: "conversation-analysis-agent"})

    # Initialize TracerProvider with the defined resource
    provider = TracerProvider(resource=resource)
    processor = export.BatchSpanProcessor(CloudTraceLoggingSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)


    server = A2AStarletteApplication(agent_card, request_handler)
    starlette_app = server.build()
    # Instrument the starlette app for tracing
    StarletteInstrumentor().instrument_app(starlette_app)
    uvicorn.run(starlette_app, host=host, port=port)


if __name__ == '__main__':
    main()
