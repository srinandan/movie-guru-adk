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

import click
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from agent_config import agent_card
from agent_executor import ConversationAnalysisAgentExecutor
from opentelemetry.instrumentation.starlette import StarletteInstrumentor
from send_metrics import setup_opentelemetry

logger = logging.getLogger(__name__)
logging.basicConfig()


@click.command()
@click.option("--host", "host", default="localhost")
@click.option("--port", "port", default=8080)
def main(host: str, port: int):
    """A2A Server."""

    # Initialize OpenTelemetry
    tracer_provider = setup_opentelemetry()

    agent_executor = ConversationAnalysisAgentExecutor()
    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor, task_store=InMemoryTaskStore()
    )

    server = A2AStarletteApplication(agent_card, request_handler)
    starlette_app = server.build()
    # Instrument the starlette app for tracing
    StarletteInstrumentor().instrument_app(
        app=starlette_app, tracer_provider=tracer_provider
    )
    uvicorn.run(starlette_app, host=host, port=port)


if __name__ == "__main__":
    main()
