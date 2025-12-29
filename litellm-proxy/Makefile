PROJECT_ID ?= $(shell gcloud config get-value project)
PROJECT_NUMBER ?= $(shell gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")
REGION ?= us-central1
_COMMIT_SHA ?= $(shell echo | sha256sum | cut -c 1-10)

local:
	docker run -it --rm --name litellm-proxy \
	-v /usr/local/google/home/srinandans/workspace/litellm/litellm_config.yaml:/app/config.yaml \
	-e GEMINI_API_KEY=${GEMINI_API_KEY} \
	-e VERTEXAI_PROJECT=${GOOGLE_CLOUD_PROJECT} \
	-e VERTEXAI_LOCATION=${GOOGLE_CLOUD_LOCATION} \
   	-p 4000:4000 \
   	docker.litellm.ai/berriai/litellm-database:main-stable \
	--config /app/config.yaml --detailed_debug

deploy:
	export _COMMIT_SHA=${_COMMIT_SHA} ;\
	export REGION=${REGION} ;\
	export PROJECT_ID=${PROJECT_ID} ;\
	export PROJECT_NUMBER=${PROJECT_NUMBER} ;\
	gcloud run deploy litellm-server \
	--project ${PROJECT_ID} \
	--region ${REGION} \
	--source . \
	--port 8080 \
	--cpu 1000m \
	--memory 1Gi \
	--concurrency 10 \
	--service-account movie-guru-chat-server-sa@${PROJECT_ID}.iam.gserviceaccount.com \
	--set-env-vars "VERTEXAI_PROJECT=${PROJECT_ID},VERTEXAI_LOCATION=${REGION},GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},DB_HOST=10.2.0.2" \
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
