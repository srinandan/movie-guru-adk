import os
from typing import Literal

import google.auth
import google.auth.transport.grpc
import google.auth.transport.requests
import grpc
from google.auth.transport.grpc import AuthMetadataPlugin

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource

# Define your sentiment types
Sentiment = Literal["SENTIMENTPOSITIVE", "SENTIMENTNEGATIVE", "SENTIMENTNEUTRAL"]

# Global variables for OpenTelemetry
_meter_provider = None
_sentiment_counter = None

otlp_endpoint = os.environ.get("OTLP_GRPC_ENDPOINT", "https://telemetry.googleapis.com") # http://localhost:4317

def setup_opentelemetry():
    """Initializes the OpenTelemetry SDK and metric exporter."""
    global _meter_provider, _sentiment_counter

    # --- 1. Configure the OTLP Exporter ---

    # Retrieve and store Google application-default credentials
    credentials, project_id = google.auth.default()
    # Request used to refresh credentials upon expiry
    request = google.auth.transport.requests.Request()

    # AuthMeatadataPlugin inserts credentials into each request
    auth_metadata_plugin = AuthMetadataPlugin(
        credentials=credentials, request=request
    )

    # Initialize gRPC channel credentials using the AuthMetadataPlugin
    channel_creds = grpc.composite_channel_credentials(
        grpc.ssl_channel_credentials(),
        grpc.metadata_call_credentials(auth_metadata_plugin),
    )

    # This exporter sends to the default OTLP endpoint:
    # http://localhost:4317 (for gRPC)
    # This is where your Ops Agent or OTel Collector should be listening.
    exporter = OTLPMetricExporter(endpoint=otlp_endpoint, credentials=channel_creds)

    # --- 2. Configure the Reader ---
    # The reader collects metrics and exports them periodically.
    reader = PeriodicExportingMetricReader(
        exporter,
        export_interval_millis=5000  # Export every 5 seconds
    )

    # --- 3. Configure the Resource ---
    # This identifies your application in Cloud Monitoring.
    resource = Resource(attributes={
        "service.name": "conversation-analysis-agent"
    })

    # --- 4. Configure the MeterProvider ---
    _meter_provider = MeterProvider(metric_readers=[reader], resource=resource)
    metrics.set_meter_provider(_meter_provider)

    # --- 5. Create the Meter and Instrument (Counter) ---
    meter = metrics.get_meter("movie-guru.sentiment.meter", "1.0.0")

    _sentiment_counter = meter.create_counter(
        name="sentiment.analysis.count",
        description="Counts the number of sentiment analysis results by type.",
        unit="1"  # "1" denotes a count
    )

    print("OpenTelemetry setup complete. Exporting to OTLP endpoint (localhost:4317)...")

def record_sentiment(sentiment: Sentiment):
    """
    Records a single sentiment analysis result as a custom metric.
    
    Args:
        sentiment: The sentiment string, must be one of the predefined types.
    """
    if not _sentiment_counter:
        print("Error: OpenTelemetry is not initialized. Call setup_opentelemetry() first.")
        return

    # These attributes become metric labels in Cloud Monitoring
    attributes = {"sentiment_type": sentiment}

    # Increment the counter by 1
    _sentiment_counter.add(1, attributes)
    print(f"Recorded metric for: {sentiment}")
