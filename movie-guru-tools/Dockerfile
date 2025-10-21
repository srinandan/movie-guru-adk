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

FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /code

# Create a non-root user
RUN adduser --disabled-password --gecos "" myuser

# Change ownership of /code to myuser
RUN chown -R myuser:myuser /code

# Switch to the non-root user
USER myuser

ENV PATH="/home/myuser/.local/bin:$PATH"

COPY --chmod=0644 --chown=myuser:myuser ./pyproject.toml ./uv.lock* ./

COPY --chmod=0644 --chown=myuser:myuser ./app ./app

# Set environment variables for uv:
# UV_COMPILE_BYTECODE=1: Compiles Python files to .pyc for faster startup
# UV_LINK_MODE=copy: Ensures files are copied, not symlinked, which can avoid issues
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install dependencies using uv sync.
# --frozen: Ensures uv respects the uv.lock file
# --no-install-project: Prevents installing the project itself in this stage
# --no-dev: Excludes development dependencies
# --mount=type=cache: Leverages Docker's build cache for uv, speeding up repeated builds
RUN --mount=type=cache,target=/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Install the project
RUN --mount=type=cache,target=/.cache/uv \
    uv sync --frozen --no-dev

ENV OTEL_SERVICE_NAME=movie-guru-mcp-server
ENV OTEL_TRACES_EXPORTER=otlp
ENV OTEL_EXPORTER_OTLP_ENDPOINT=https://telemetry.googleapis.com


EXPOSE 8080

CMD ["uv", "run", "-m", "app.server"]