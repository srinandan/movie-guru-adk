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

import json
import logging
import datetime
import vertexai
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
import psycopg2
import os
from typing import List, Dict, Any, Optional
from pgvector.psycopg2 import register_vector
from google.cloud import storage

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.exceptions import ToolError

from google import auth
from google.auth.transport import requests
from google.auth.transport.grpc import AuthMetadataPlugin
from google.auth import default, compute_engine
import grpc

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

mcp = FastMCP("Movie Guru Tools")

_, project_id = auth.default()
PROJECT_ID = os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)


# Initialize Vertex AI
vertexai.init(project=os.getenv("GOOGLE_CLOUD_PROJECT"),
              location=os.getenv("GOOGLE_CLOUD_LOCATION"))

# Load the embedding model
embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")

top_k = 5

conn = None

os.environ['GOOGLE_CLOUD_QUOTA_PROJECT']=f"{PROJECT_ID}"
os.environ['OTEL_RESOURCE_ATTRIBUTES'] = f"gcp.project_id={PROJECT_ID}"
os.environ['OTEL_SERVICE_NAME']="movie-guru-mcp-server"
os.environ['OTEL_TRACES_EXPORTER']="otlp"
os.environ['OTEL_EXPORTER_OTLP_ENDPOINT']="https://telemetry.googleapis.com"

# Define the service name
resource = Resource.create(
    attributes={
        SERVICE_NAME: "movie-guru-mcp-server",
    }
)

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

# Initialize OpenTelemetry TracerProvider
tracer_provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(otlp_grpc_exporter)
tracer_provider.add_span_processor(processor)
trace.set_tracer_provider(tracer_provider)

bucket_name = os.getenv("BUCKET_NAME")
if not bucket_name:
    gcp_project = os.getenv("GOOGLE_CLOUD_PROJECT")
    if gcp_project:
        bucket_name = f"{gcp_project}_posters"

class TraceMiddleware(Middleware):
    async def on_call_tool(self, context: MiddlewareContext, call_next):

        tool_name = context.message.name

        # The tracer name can be any string. Using the module name is a common practice.
        tracer = trace.get_tracer(__name__)
        span_name = tool_name

        with tracer.start_as_current_span(span_name) as span:
            # Add attributes to the span for more context in Cloud Trace.
            span.set_attribute("context.method", str(context.method))
            span.set_attribute("context.name", str(context.message.name))
            span.set_attribute("context.type", str(context.type))
            span.set_attribute("service.name", "movie-guru-mcp-server")
            # Allow other tools to proceed
            return await call_next(context)


mcp.add_middleware(TraceMiddleware())

def connect_to_movie_db(dbname: str,
                        user: str,
                        password: str,
                        host: str,
                        port: str = "5432") -> Any:
    """
    Establishes a connection to a PostgreSQL database with pgvector enabled.

    Args:
        dbname: The name of your PostgreSQL database.
        user: The username to connect to the database.
        password: The password for the user.
        host: The host of your Cloud SQL instance (e.g., your public IP or connection name).
        port: The port number for the database connection (default is 5432).

    Returns:
        Any: A psycopg2 connection object if successful.

    Raises:
        psycopg2.Error: If an error occurs during the database connection.
    """
    conn_params = {
        "dbname": dbname,
        "user": user,
        "password": password,
        "host": host,
        "port": port
    }
    conn = None

    try:
        conn = psycopg2.connect(**conn_params)
        # Register the pgvector type with psycopg2 to enable vector operations
        register_vector(conn)
        print("Successfully connected to PostgreSQL database.")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        raise  # Re-raise the exception to indicate connection failure


@mcp.tool()
def search_movies_by_embedding(query_text: str) -> List[Dict[str, Any]]:
    """
    Performs a vector similarity search for movies in the 'movies' table.

    Args:
        query_text: the query text from the user.

    Returns:
        A list of dictionaries, where each dictionary represents a movie
        and includes its original data along with a similarity score (if applicable
        and calculated by the query).
    """
    global conn

    if conn is None:
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        if db_password is None or db_host is None:
            raise ValueError(
                "DB_PASSWORD or DB_HOST environment variable not set.")
        conn = connect_to_movie_db(dbname="fake-movies-db",
                                   user="postgres",
                                   password=db_password,
                                   host=db_host,
                                   port="5432")

    print(
        f"Agent is using Cloud SQL PostgreSQL retrieval tool for query: '{query_text}'"
    )

    # Generate embedding for the query using Vertex AI
    query_embedding_input = TextEmbeddingInput(text=query_text,
                                               task_type="RETRIEVAL_QUERY")
    query_embedding_response = embedding_model.get_embeddings(
        [query_embedding_input])
    query_embedding = query_embedding_response[0].values

    results = []
    try:
        with conn.cursor() as cur:
            query = """
            SELECT
                tconst,
                title,
                runtime_mins,
                genres,
                rating,
                released,
                actors,
                director,
                plot,
                poster,
                content
            FROM movies
            ORDER BY embedding <-> %s::vector
            LIMIT %s;
            """
            cur.execute(query, (query_embedding, top_k))
            rows = cur.fetchall()

            # Get column names from cursor description
            column_names = [desc[0] for desc in cur.description]

            for row in rows:
                movie_data = dict(zip(column_names, row))
                poster_blob_name = movie_data.get("poster")
                if poster_blob_name and bucket_name:
                    movie_data["poster"] = generate_download_signed_url_v4(
                        bucket_name, poster_blob_name)
                results.append(movie_data)

    except psycopg2.Error as e:
        print(f"Error during vector search: {e}")
        # Depending on agent framework, you might raise an exception or return an empty list
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
    return results


@mcp.tool()
def get_user_preferences() -> dict:
    """
    Retrieves user preferences from a PostgreSQL database.

    Args:
        username: The username for whom to retrieve preferences.

    Returns:
        A dictionary representing the user's preferences, or None if not found or an error occurs.
    """
    global conn

    headers = get_http_headers()
    user = headers.get("x-user-id", "")
    print(f"Getting preferences for user: {user}")

    if user == "":
        return {}

    if conn is None:
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        if db_password is None or db_host is None:
            raise ValueError(
                "DB_PASSWORD or DB_HOST environment variable not set.")
        conn = connect_to_movie_db(dbname="fake-movies-db",
                                   user="postgres",
                                   password=db_password,
                                   host=db_host,
                                   port="5432")

    try:
        with conn.cursor() as cur:
            # Execute the query
            query = "SELECT \"preferences\" FROM \"user_preferences\" WHERE \"user\" = %s;"
            print(query)
            cur.execute(query, (user, ))

            # Fetch the result
            result = cur.fetchone()

            if result:
                return result[0]
            else:
                print(f"No preferences found for user: {user}")
                return {}
    except psycopg2.Error as e:
        print(f"Error during user preferences search: {e}")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {}


@mcp.tool()
def create_or_update_user_preferences(preferences: dict) -> bool:
    """
    Creates or updates user preferences in a PostgreSQL table.

    Args:
        preferences (dict): A dictionary representing the user's preferences.
                            Expected schema:
                            {
                                "likes": {"actors": [], "directors": [], "genres": [], "others": []},
                                "dislikes": {"actors": [], "directors": [], "genres": [], "others": []}
                            }

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    global conn

    headers = get_http_headers()
    user = headers.get("x-user-id", "")
    print(f"Creating preferences for user: {user}")

    if not user:
        print("User id was not present in the header.")
        return False

    if conn is None:
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        if db_password is None or db_host is None:
            raise ValueError(
                "DB_PASSWORD or DB_HOST environment variable not set.")
        conn = connect_to_movie_db(dbname="fake-movies-db",
                                   user="postgres",
                                   password=db_password,
                                   host=db_host,
                                   port="5432")
    try:

        with conn.cursor() as cur:

            upsert_query = """
            INSERT INTO "user_preferences" ("user", "preferences")
            VALUES (%s, %s)
            ON CONFLICT ("user") DO UPDATE SET
                "preferences" = EXCLUDED.preferences;
            """
            cur.execute(upsert_query, (user, json.dumps(preferences)))
            print(f"Preferences upserted successfully for user: {user}")

            # Commit the transaction
            conn.commit()
            return True

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()  # Rollback in case of error
        return False
    except json.JSONDecodeError as e:
        print(f"JSON encoding error: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False


def generate_download_signed_url_v4(bucket_name, blob_name):
    """Generates a v4 signed URL for downloading a blob using ADC.
    """
    if not blob_name:
        blob_name = "notfound.png"

    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"

    # Set the expiration time for the URL.
    url_expiration = datetime.timedelta(minutes=15)

    try:
        credentials, project = auth.default()
        credentials.refresh(auth.transport.requests.Request())

        storage_client = storage.Client(credentials=credentials,
                                        project=project)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

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


@mcp.tool()
def get_random_movies() -> List[Dict[str, Any]]:
    """
    Retrieves 5 random movies from the 'movies' table.

    Returns:
        A list of dictionaries, where each dictionary represents a movie
        and includes its title and a signed URL for its poster.
    """
    global conn

    if conn is None:
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        if db_password is None or db_host is None:
            raise ValueError(
                "DB_PASSWORD or DB_HOST environment variable not set.")
        conn = connect_to_movie_db(dbname="fake-movies-db",
                                   user="postgres",
                                   password=db_password,
                                   host=db_host,
                                   port="5432")

    print("Agent is using get_random_movies tool.")

    results = []
    try:
        with conn.cursor() as cur:
            query = """
            SELECT title, poster
            FROM movies
            ORDER BY RANDOM()
            LIMIT 3;
            """
            cur.execute(query)
            rows = cur.fetchall()

            for row in rows:
                title, poster_blob_name = row
                signed_poster_url = generate_download_signed_url_v4(
                    bucket_name, poster_blob_name
                ) if poster_blob_name and bucket_name else None
                results.append({"title": title, "poster": signed_poster_url})

    except psycopg2.Error as e:
        print(f"Error during random movie retrieval: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
    return results


if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8080)
