PROJECT_ID ?= $(shell gcloud config get-value project)
REGION ?= us-central1
SERVICE_NAME = movie-chatbot

.PHONY: build deploy

build:
	@echo "Building Docker image for $(SERVICE_NAME)..."
	docker build -t $(REGION)-docker.pkg.dev/$(PROJECT_ID)/movie-guru-repo/$(SERVICE_NAME) .


backend:
	@echo "Deploying $(SERVICE_NAME) to Cloud Run..."
	gcloud run deploy $(SERVICE_NAME) \
		--project $(PROJECT_ID) \
		--region $(REGION) \
		--source . \
		--port 8080 \
		--allow-unauthenticated \
		--timeout 300 \
		--cpu-boost \
		--session-affinity \
		--cpu 1000m \
		--memory 1Gi \
		--concurrency 10 \
		--service-account movie-guru-chat-server-sa@${PROJECT_ID}.iam.gserviceaccount.com \
		--set-env-vars VITE_API_BASE_URL="https://movieguruagent.endpoints.srinandans-next25-demo.cloud.goog,OTEL_SERVICE_NAME=movie-chatbot" \
		--cpu-boost \
		--vpc-egress all \
		--network movie-guru-network \
		--subnet movie-guru-subnet \
		--max-instances 1 \
		--min-instances 1 \
		--ingress internal-and-cloud-load-balancing \
		--build-worker-pool="projects/${PROJECT_ID}/locations/${REGION}/workerPools/movie-guru"
