PROJECT_ID ?= $(shell gcloud config get-value project)
REGION ?= us-central1
SERVICE_NAME = movie-guru-loadgen

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
		--set-env-vars "PROMPT_SERVER=https://ollama-gemma-432423772502.us-central1.run.app,CHAT_SERVER=https://movie-guru-agent-432423772502.us-central1.run.app" \
		--cpu-boost \
		--vpc-egress all \
		--network movie-guru-network \
		--subnet movie-guru-subnet \
		--max-instances 1 \
		--min-instances 1 \
		--ingress internal-and-cloud-load-balancing \
		--labels=appid=movie-guru-adk \
		--build-worker-pool="projects/${PROJECT_ID}/locations/${REGION}/workerPools/movie-guru"
