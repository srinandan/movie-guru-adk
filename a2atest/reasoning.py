import os
import google.auth
import vertexai
from google.genai import types

credentials, project_id = google.auth.default()

PROJECT_ID = os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
LOCATION = os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
RESOURCE_ID = "5101931864973639680"
RESOURCE_NAME = f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{RESOURCE_ID}"

client = vertexai.Client(
    project=PROJECT_ID,
    location=LOCATION,
    http_options=types.HttpOptions(api_version="v1beta1")
)

remote_agent = client.agent_engines.get(name=RESOURCE_NAME)

response = remote_agent.handle_authenticated_agent_card()

message_data = {
  "messageId": "remote-agent-message-id",
  "role": "user",
  "parts": [{"kind": "text", "text": "Can you recommend a few movies?"}],
}

response = remote_agent.on_message_send(**message_data)

print(response)