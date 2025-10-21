install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/0.6.12/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync --dev --extra jupyter --frozen

backend:
	PROJECT_ID=$$(gcloud config get-value project) && \
	PROJECT_NUMBER=$$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)") && \
	gcloud run deploy movie-guru-mcp-server \
	--project ${PROJECT_ID} \
	--region ${REGION} \
	--source . \
	--port 8080 \
	--cpu 1000m \
	--memory 1Gi \
	--concurrency 10 \
	--service-account movie-guru-chat-server-sa@${PROJECT_ID}.iam.gserviceaccount.com \
	--set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},DB_HOST=10.2.0.2,BUCKET_NAME=${PROJECT_ID}_posters" \
	--startup-probe="initialDelaySeconds=30,tcpSocket.port=8080,timeoutSeconds=240,periodSeconds=240,failureThreshold=1" \
	--max-instances 1 \
	--allow-unauthenticated \
	--timeout 300 \
	--cpu-boost \
	--session-affinity \
	--vpc-egress private-ranges-only \
	--network movie-guru-network \
	--subnet movie-guru-subnet \
	--set-secrets="DB_PASSWORD=postgres-root-password-secret:latest" \
	--ingress internal-and-cloud-load-balancing	

deploy:
	PROJECT_ID=$(gcloud config get-value project) && \
	gcloud builds submit \
		--config=./deployment/cd/dev-cloudrun.yaml \
		--project ${PROJECT_ID} \
		--region ${REGION} \
		--worker-pool="projects/${PROJECT_ID}/locations/${REGION}/workerPools/movie-guru"
		--substitutions=_SHORT_SHA=$(echo | sha256sum | cut -c 1-10)

local-backend:
	uv run app.server:app --host 0.0.0.0 --port 8080 --reload

lint:
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run mypy .	