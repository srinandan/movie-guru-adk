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
from agent_config import agent_card
from agent_executor import ConversationAnalysisAgentExecutor
from opentelemetry.instrumentation.starlette import StarletteInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

import google.auth
import google.auth.transport.grpc
import google.auth.transport.requests
import grpc
from google.auth.transport.grpc import AuthMetadataPlugin


logger = logging.getLogger(__name__)
logging.basicConfig()

_, project_id = google.auth.default()
PROJECT_ID = os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)

REGION = os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
VERTEX_AI = os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

os.environ['GOOGLE_CLOUD_QUOTA_PROJECT']=f"{PROJECT_ID}"
os.environ['OTEL_RESOURCE_ATTRIBUTES'] = f"gcp.project_id={PROJECT_ID}"

# Define the service name
resource = Resource.create(
    attributes={
        # Use the PID as the service.instance.id to avoid duplicate timeseries
        # from different Gunicorn worker processes.
        SERVICE_NAME: "conversation-analysis-agent",
    }
)

# Set up OpenTelemetry Python SDK
# Retrieve and store Google application-default credentials
credentials, project_id = google.auth.default()
# Request used to refresh credentials upon expiry
request = google.auth.transport.requests.Request()

# Supply the request and credentials to AuthMetadataPlugin
# AuthMeatadataPlugin inserts credentials into each request
auth_metadata_plugin = AuthMetadataPlugin(
    credentials=credentials, request=request
)

# Initialize gRPC channel credentials using the AuthMetadataPlugin
channel_creds = grpc.composite_channel_credentials(
    grpc.ssl_channel_credentials(),
    grpc.metadata_call_credentials(auth_metadata_plugin),
)

otlp_grpc_exporter = OTLPSpanExporter(credentials=channel_creds)

# Initialize OpenTelemetry TracerProvider
tracer_provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(otlp_grpc_exporter)
tracer_provider.add_span_processor(processor)
trace.set_tracer_provider(tracer_provider)


@click.command()
@click.option('--host', 'host', default='localhost')
@click.option('--port', 'port', default=8080)
def main(host: str, port: int):
    """A2A Server."""
    agent_executor = ConversationAnalysisAgentExecutor()
    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor, task_store=InMemoryTaskStore()
    )

    server = A2AStarletteApplication(agent_card, request_handler)
    starlette_app = server.build()
    # Instrument the starlette app for tracing
    StarletteInstrumentor().instrument_app(starlette_app)
    uvicorn.run(starlette_app, host=host, port=port)


if __name__ == '__main__':
    main()
