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
