# Copyright 2026 Google LLC
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

# Use the provided base image
FROM ghcr.io/berriai/litellm:main-latest

# Set the working directory to /app
WORKDIR /app

RUN pip install --upgrade certifi
RUN pip install opentelemetry-distro opentelemetry-exporter-otlp
RUN opentelemetry-bootstrap -a install

# Copy the configuration file into the container at /app
COPY litellm_config.yaml .

ENV OTEL_SERVICE_NAME=litellm-proxy
ENV OTEL_TRACES_EXPORTER=otlp
ENV OTEL_EXPORTER_OTLP_ENDPOINT=https://telemetry.googleapis.com

#RUN sed -i 's|exec litellm "$@"|exec opentelemetry-instrument --traces_exporter console --metrics_exporter none --logs_exporter none litellm "$@"|g' /docker/prod_entrypoint.sh

# Expose the necessary port
EXPOSE 8080/tcp

CMD ["--port", "8080", "--config", "litellm_config.yaml"]
