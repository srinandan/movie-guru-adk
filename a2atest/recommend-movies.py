
import os
import asyncio
import vertexai
import google.auth

_, project_id = google.auth.default()
PROJECT_ID = os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
LOCATION = os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
RESOURCE_ID="1173413102813708288"
REASONING_ENGINE=f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{RESOURCE_ID}"

client = vertexai.Client(  # For service interactions via client.agent_engines
    project=PROJECT_ID,
    location=LOCATION,
)

async def main():
    adk_app = client.agent_engines.get(name=REASONING_ENGINE)

    session = await adk_app.async_create_session(user_id="fake")

    print(session)

    async for event in adk_app.async_stream_query(
        user_id="fake",
        session_id=session['id'],
        message="Can you recommend a few action movies?",
    ):
      print(event)


# Main execution
if __name__ == "__main__":
    asyncio.run(main())