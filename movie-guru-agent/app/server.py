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

import os
import datetime
import psycopg2
from google.cloud import storage
from google import auth
from typing import Annotated, Union, List, Dict, Any

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Header, status, Response, HTTPException
from fastapi.responses import JSONResponse
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.sessions import DatabaseSessionService, Session
from google.adk.memory import InMemoryMemoryService
from google.adk.events import Event

from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider, export
from google.auth.transport import requests
from google.auth.transport.grpc import AuthMetadataPlugin
import grpc

from app.utils.gcs import create_bucket_if_not_exists
from app.utils.context import user_id_context
from app.utils.tracing import CloudTraceLoggingSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from app.utils.typing import Feedback
from app.utils.envvars import PROJECT_ID, REGION, DB_HOST, DB_NAME, DB_PASSWORD, POSTER_DIRECTORY
from app.utils.logging import logger

allow_origins = (os.getenv("ALLOW_ORIGINS", "").split(",")
                 if os.getenv("ALLOW_ORIGINS") else None)

bucket_name = f"gs://{PROJECT_ID}"
create_bucket_if_not_exists(bucket_name=bucket_name,
                            project=PROJECT_ID,
                            location=REGION)

posters_bucket_name = f"{PROJECT_ID}_posters"

os.environ['GOOGLE_CLOUD_QUOTA_PROJECT']=f"{PROJECT_ID}"
os.environ['OTEL_RESOURCE_ATTRIBUTES'] = f"gcp.project_id={PROJECT_ID}"
os.environ['OTEL_SERVICE_NAME']="movie-guru-agent"
os.environ['OTEL_TRACES_EXPORTER']="otlp"
os.environ['OTEL_EXPORTER_OTLP_ENDPOINT']="https://telemetry.googleapis.com"

# Define the service name
resource = Resource(attributes={SERVICE_NAME: "movie-guru-agent"})

# Set up OpenTelemetry Python SDK
# Retrieve and store Google application-default credentials
credentials, project_id = auth.default()
# Request used to refresh credentials upon expiry
request = auth.transport.requests.Request()

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

# Initialize TracerProvider with the defined resource
provider = TracerProvider(resource=resource)
#processor = export.BatchSpanProcessor(CloudTraceLoggingSpanExporter())
processor = BatchSpanProcessor(otlp_grpc_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# "sqlite:///./sessions.db"
SESSION_DB_URL = (
    f"postgresql+pg8000://postgres:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}")

db_conn = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Logs all environment variables at application startup, redacting secrets."""
    logger.log("--- Environment Variables ---")
    for key, value in sorted(os.environ.items()):
        if any(secret in key.upper() for secret in
               ["PASSWORD", "SECRET", "API_KEY", "TOKEN", "DB_PASSWORD"]):
            value = "********"
        logger.log(f"{key}: {value}")
    logger.log("---------------------------")
    yield


# Initialize DatabaseSessionService
session_service = DatabaseSessionService(db_url=SESSION_DB_URL)

memory_service = InMemoryMemoryService()  # Initialize MemoryService

app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=False,
    artifact_service_uri=bucket_name,
    session_service_uri=SESSION_DB_URL,
    allow_origins=allow_origins,
    trace_to_cloud=True,
    otel_to_cloud=False,
    lifespan=lifespan,
)

app.title = "movie-guru-agent"

@app.middleware("http")
async def add_root_span_for_request(request: Request, call_next):
    """
    This middleware creates a parent trace span for each incoming request,
    and sets the user ID in a context variable for the request.
    This helps in grouping all the operations for a single request under one trace.
    """
    user_id = "fake"
    if hasattr(request.state, "session_user_id"):
        user_id = request.state.session_user_id
    else:
        # Extract the user email from the header. This requires IAP to be setup
        user_email = request.headers.get("x-goog-authenticated-user-email")
        if user_email:
            user_id = user_email.split(":")[-1]
            user_id_context.set(user_id)

    try:
        # The tracer name can be any string. Using the module name is a common practice.
        tracer = trace.get_tracer(__name__)
        span_name = f"HTTP {request.method} {request.url.path}"

        with tracer.start_as_current_span(span_name) as span:
            # Add attributes to the span for more context in Cloud Trace.
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.url", str(request.url))
            span.set_attribute("user.id", user_id)
            span.set_attribute("service.name", "movie-guru-agent")
            response = await call_next(request)
            span.set_attribute("http.status_code", response.status_code)
            return response
    finally:
        logger.log(f"User ID set in context: {user_id}")


@app.post("/sessions")
async def start_user_session(
    x_user_id: Annotated[Union[str, None],
                         Header(
                             alias="x-goog-authenticated-user-email")] = None):
    """
    Starts a new session for the user identified by X-User-ID header.
    """
    if not x_user_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "User login is required to start a session."})

    # You can generate a session_id or use a consistent one per user/app
    # For a new conversation, a unique session_id is usually generated.
    # For persistent sessions across multiple conversations for the same user,
    # you might derive session_id from user_id or retrieve an existing one.
    # Example: unique session per request
    
    # Get today's date
    today = datetime.date.today()
    ts = today.strftime("%y%m%d")
    session_id = f"session_{x_user_id}_{ts}"
    user_id = x_user_id.split(":")[-1]

    try:
        # Attempt to get an existing session for this user/session_id
        session = await session_service.get_session(app_name="app",
                                                    user_id=user_id,
                                                    session_id=session_id)
        if not session:
            # If no session exists, create a new one, passing the extracted user_id
            session = await session_service.create_session(
                app_name="app",
                user_id=user_id,
                session_id=session_id,
            )
            message = "New session created."
        else:
            message = "Existing session retrieved."

        # Add the session to the memory service
        await memory_service.add_session_to_memory(session)

        return JSONResponse(
            content={
                "message": message,
                "session_id": session.id,
                "user_id": session.user_id,
                "app_name": session.app_name
            })
    except Exception as e:
        print(f"Error managing session: {e}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content={"message": "Failed to manage session."})


@app.post("/sessions/{session_id}/events")
async def add_event_to_session(
    session_id: str,
    event_data: dict,  # Expecting a dictionary for event data
    x_user_id: Annotated[Union[str, None],
                         Header(
                             alias="x-goog-authenticated-user-email")] = None):
    if not x_user_id:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                            content={"message": "User login is required."})

    try:
        user_id = x_user_id.split(":")[-1]
        session = await session_service.get_session(app_name="app",
                                                    user_id=user_id,
                                                    session_id=session_id)
        if not session or session.user_id != x_user_id:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "message":
                    "Session not found or does not belong to this user."
                })

        # Assuming event_data contains a 'text' field for a simple message event
        new_event = Event(author="user", )
        await session_service.append_event(session=session, event=new_event)
        return JSONResponse(content={"message": "Event added successfully."})

    except Exception as e:
        print(f"Error adding event: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Failed to add event to session."})


@app.get("/posters/{poster_id}")
async def get_poster(poster_id: str):
    """
    Retrieves the content of a PNG poster by its ID.

    Args:
        poster_id (str): The ID of the poster, which should correspond to the
                         filename (without the .png extension) of the image.

    Returns:
        Response: The content of the PNG file with 'image/png' media type.

    Raises:
        HTTPException: If the poster file is not found.
    """
    # Construct the full file path. We assume the poster_id is the base filename.
    file_path = os.path.join(POSTER_DIRECTORY, f"{poster_id}.png")

    # Check if the file exists and is a file
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404,
                            detail=f"Poster '{poster_id}.png' not found.")

    try:
        # Read the file content in binary mode
        with open(file_path, "rb") as f:
            content = f.read()

        # Return the content with the appropriate media type
        return Response(content=content, media_type="image/png")
    except Exception as e:
        # Handle any other potential errors during file reading
        raise HTTPException(status_code=500,
                            detail=f"Error reading poster file: {e}")


def generate_download_signed_url_v4(blob_name):
    """Generates a v4 signed URL for downloading a blob using ADC.
    """
    if not blob_name:
        blob_name = "notfound.png"

    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"

    # Set the expiration time for the URL.
    url_expiration = datetime.timedelta(minutes=15)

    try:

        logger.log(
            f"the bucket is {posters_bucket_name} and the poster is {blob_name}"
        )

        credentials, project = auth.default()
        credentials.refresh(auth.transport.requests.Request())

        storage_client = storage.Client(credentials=credentials,
                                        project=project)
        bucket = storage_client.bucket(posters_bucket_name)
        blob = bucket.blob(blob_name)

        logger.log(
            f"the service account is {credentials.service_account_email}")

        # Generate the signed URL.
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=url_expiration,
            service_account_email=credentials.service_account_email,
            method="GET",
            access_token=credentials.token,
        )
        return signed_url
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


@app.get("/random")
async def get_random_movies() -> List[Dict[str, Any]]:
    """
    Retrieves 5 random movies from the 'movies' table directly from the database.

    Returns:
        A list of dictionaries, where each dictionary represents a movie
        and includes its title and a signed URL for its poster.
    """
    global db_conn
    if not db_conn:
        db_conn = psycopg2.connect(dbname=DB_NAME,
                                   user="postgres",
                                   password=DB_PASSWORD,
                                   host=DB_HOST,
                                   port="5432")

    results = []
    try:
        with db_conn.cursor() as cur:
            query = """
            SELECT title, poster
            FROM movies
            ORDER BY RANDOM()
            LIMIT 3;
            """
            cur.execute(query)
            rows = cur.fetchall()

            # Get column names from cursor description
            column_names = [desc[0] for desc in cur.description]

            for row in rows:
                movie_data = dict(zip(column_names, row))
                poster_blob_name = movie_data.get("poster")
                title = movie_data.get("title")
                signed_poster_url = generate_download_signed_url_v4(
                    poster_blob_name)
                results.append({"title": title, "poster": signed_poster_url})
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Error fetching random movies: {e}")
    return results


app.description = "API for interacting with the Agent movie-guru-agent"
app.version = "0.1.0"

# Main execution
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
