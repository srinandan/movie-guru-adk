import os
import google.auth
import asyncio
import vertexai
from google.genai import types

credentials, project_id = google.auth.default()

PROJECT_ID = os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
LOCATION = os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
RESOURCE_ID="2733910373697585152"
REASONING_ENGINE=f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{RESOURCE_ID}"

client = vertexai.Client(
    project=PROJECT_ID,
    location=LOCATION,
    http_options=types.HttpOptions(api_version="v1beta1"))


remote_agent = client.agent_engines.get(name=REASONING_ENGINE)

import uuid

async def main():
    agent_card = await remote_agent.handle_authenticated_agent_card()
    print(agent_card)

    message_data = {
        "messageId": str(uuid.uuid4()),
        "role": "user",
        "parts": [{"kind": "text", "text": "Can you recommend movies?"}],
        "contextId": "remote-agent-context-id",
    }

    try:
        response = await remote_agent.on_message_send(**message_data)
        print(response)
    except Exception as e:
        print(f"Error occurred: {type(e).__name__}: {e}")
        # Try to find the original httpx error which has the response text
        curr = e
        while curr is not None:
            if hasattr(curr, 'response'):
                print(f"Response status: {curr.response.status_code}")
                print(f"Response text: {curr.response.text}")
                break
            curr = curr.__cause__ if hasattr(curr, '__cause__') else None
        raise e

if __name__ == "__main__":
    asyncio.run(main())
