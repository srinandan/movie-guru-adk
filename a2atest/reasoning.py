import os
import google.auth
import asyncio
import vertexai
from google.genai import types

credentials, project_id = google.auth.default()

PROJECT_ID = os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
LOCATION = os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
RESOURCE_ID="6699794939015856128"
REASONING_ENGINE=f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{RESOURCE_ID}"

client = vertexai.Client(
    project=PROJECT_ID,
    location=LOCATION,
    http_options=types.HttpOptions(api_version="v1beta1"))


remote_agent = client.agent_engines.get(name=REASONING_ENGINE)

async def main():
    agent_card = await remote_agent.handle_authenticated_agent_card()
    print(agent_card)

if __name__ == "__main__":
    asyncio.run(main())
