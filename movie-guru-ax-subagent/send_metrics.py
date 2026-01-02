import logging
import uuid
import os
from typing import Literal

import google.auth
import google.auth.transport.grpc
import google.auth.transport.requests
import grpc
from google.auth.transport.grpc import AuthMetadataPlugin
from opentelemetry import metrics, trace
from opentelemetry.exporter.cloud_monitoring import CloudMonitoringMetricsExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_INSTANCE_ID, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Define your sentiment types
Sentiment = Literal["SENTIMENTPOSITIVE", "SENTIMENTNEGATIVE", "SENTIMENTNEUTRAL"]

_sentiment_counter = None

def setup_opentelemetry() -> TracerProvider:
    global _sentiment_counter
    
    # Retrieve and store Google application-default credentials
    credentials, project_id = google.auth.default()
    PROJECT_ID = os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)

    # Set up OpenTelemetry environment variables
    os.environ['OTEL_EXPORTER_GCP_MONITORING_PROJECT_ID'] = f"{PROJECT_ID}"
    os.environ['GOOGLE_CLOUD_QUOTA_PROJECT'] = f"{PROJECT_ID}"
    os.environ['OTEL_RESOURCE_ATTRIBUTES'] = f"gcp.project_id={PROJECT_ID}"
    os.environ['OTEL_SPAN_ATTRIBUTE_VALUE_LENGTH_LIMIT'] = "512"
    os.environ['OTEL_SERVICE_NAME'] = "conversation-analysis-agent"
    os.environ['OTEL_EXPORTER_OTLP_ENDPOINT'] = "https://telemetry.googleapis.com"
    os.environ['OTEL_TRACES_EXPORTER'] = "otlp"

    # Define the service name
    resource = Resource.create(
        attributes={
            SERVICE_NAME: "conversation-analysis-agent",
            # Required for generic_task -> namespace
            "service.namespace": "default",
            # Required for generic_task -> task_id (must be unique per running instance)
            SERVICE_INSTANCE_ID: f"worker-{os.getpid()}",
            # Required for generic_task -> location
            "cloud.availability_zone": "global",
            "gcp.project_id": PROJECT_ID,
        }
    )

    # Request used to refresh credentials upon expiry
    request = google.auth.transport.requests.Request()

    # Supply the request and credentials to AuthMetadataPlugin
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

    # Initialize OpenTelemetry MeterProvider
    metrics.set_meter_provider(
        MeterProvider(
            metric_readers=[
                PeriodicExportingMetricReader(
                    CloudMonitoringMetricsExporter(), export_interval_millis=5000
                )
            ],
            resource=resource,
        )
    )

    meter = metrics.get_meter(__name__)

    _sentiment_counter = meter.create_counter(
        name="sentiment.analysis.count",
        description="Counts the number of sentiment analysis results by type.",
        unit="1"
    )
    
    return tracer_provider


def record_sentiment(sentiment: Sentiment):
    """
    Records a single sentiment analysis result as a custom metric.
    
    Args:
        sentiment: The sentiment string, must be one of the predefined types.
    """
    global _sentiment_counter
    
    if _sentiment_counter is None:
        print("Warning: _sentiment_counter is not initialized. Call setup_opentelemetry() first.")
        return

    # These attributes become metric labels in Cloud Monitoring
    attributes = {"sentiment_type": sentiment}

    # Increment the counter by 1
    _sentiment_counter.add(1, attributes)
    print(f"Recorded metric for: {sentiment}")
