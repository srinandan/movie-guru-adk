import os
import time
from typing import Literal

from google.cloud import monitoring_v3

# Define the allowed sentiment types for type hinting
Sentiment = Literal["SENTIMENTPOSITIVE", "SENTIMENTNEGATIVE", "SENTIMENTNEUTRAL"]

def send_custom_sentiment_metric(project_id: str, sentiment: Sentiment):
    """Sends a custom sentiment metric to Google Cloud Monitoring.

    This function sends a data point with a value of 1 for the specified
    sentiment. The metric is a DELTA, meaning it represents the change in a
    value over a time interval. This is ideal for counting event occurrences.

    Args:
        project_id (str): Your Google Cloud project ID.
        sentiment (str): The sentiment to record. Must be one of
                         'SENTIMENTPOSITIVE', 'SENTIMENTNEGATIVE', or 'SENTIMENTNEUTRAL'.
    """
    # Create a client for the Google Cloud Monitoring API
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"

    # Map the input sentiment to a user-friendly label
    sentiment_map = {
        "SENTIMENTPOSITIVE": "positive",
        "SENTIMENTNEGATIVE": "negative",
        "SENTIMENTNEUTRAL": "neutral",
    }

    if sentiment not in sentiment_map:
        print(f"Error: Invalid sentiment value '{sentiment}'. Aborting.")
        print("Please use one of 'SENTIMENTPOSITIVE', 'SENTIMENTNEGATIVE', or 'SENTIMENTNEUTRAL'.")
        return

    sentiment_label = sentiment_map[sentiment]

    # Prepare the time series data
    series = monitoring_v3.TimeSeries()

    # Define the custom metric type and its labels
    series.metric.type = "custom.googleapis.com/user_sentiment_count"
    series.metric.labels["sentiment_type"] = sentiment_label

    # Associate the metric with a monitored resource.
    # Using "global" is a good default for metrics not tied to a specific VM or service.
    series.resource.type = "global"
    series.resource.labels["project_id"] = project_id

    # The metric kind is DELTA, as we are counting individual events.
    series.metric_kind = monitoring_v3.MetricDescriptor.MetricKind.DELTA
    series.value_type = monitoring_v3.MetricDescriptor.ValueType.INT64

    # Create a data point. For a DELTA, we specify an interval.
    # For a single event, the start and end time can be the same.
    now = time.time()
    seconds = int(now)
    nanos = int((now - seconds) * 10**9)

    interval = monitoring_v3.TimeInterval(
        {
            "start_time": {"seconds": seconds, "nanos": nanos},
            "end_time": {"seconds": seconds, "nanos": nanos},
        }
    )
    # The value of the data point is 1, representing one occurrence of this sentiment.
    point = monitoring_v3.Point({"interval": interval, "value": {"int64_value": 1}})
    series.points = [point]

    try:
        # Send the time series data to Cloud Monitoring
        client.create_time_series(name=project_name, time_series=[series])
        print(f"Successfully sent '{sentiment_label}' sentiment metric to Cloud Monitoring.")
    except Exception as e:
        print(f"Error sending metric to Cloud Monitoring: {e}")