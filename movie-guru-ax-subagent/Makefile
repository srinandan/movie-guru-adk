backend:
	PROJECT_ID=$$(gcloud config get-value project) && \
	PROJECT_NUMBER=$$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)") && \
	gcloud run deploy conversation-analysis-agent \
	--project ${PROJECT_ID} \
	--region ${REGION} \
	--source . \
	--port 8080 \
	--cpu 1000m \
	--memory 1Gi \
	--concurrency 10 \
	--service-account movie-guru-chat-server-sa@${PROJECT_ID}.iam.gserviceaccount.com \
	--startup-probe="initialDelaySeconds=30,tcpSocket.port=8080,timeoutSeconds=240,periodSeconds=240,failureThreshold=1" \
	--set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},MODEL=ollama,API_BASE=https://ollama-gemma-${PROJECT_NUMBER}.${REGION}.run.app" \
	--max-instances 1 \
	--allow-unauthenticated \
	--timeout 300 \
	--cpu-boost \
	--session-affinity \
	--vpc-egress private-ranges-only \
	--network movie-guru-network \
	--subnet movie-guru-subnet \
	--ingress internal-and-cloud-load-balancing \
	--build-worker-pool="projects/${PROJECT_ID}/locations/${REGION}/workerPools/movie-guru"

local-backend:
	uv run .

agent-engine:
	# Export dependencies to requirements file using uv export.
	uv export --no-hashes --no-header --no-dev --no-emit-project --no-annotate --frozen > .requirements.txt 2>/dev/null || \
	uv export --no-hashes --no-header --no-dev --no-emit-project --frozen > .requirements.txt && uv run agent_engine_app.py --project=$${PROJECT_ID}