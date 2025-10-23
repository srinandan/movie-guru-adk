backend:
	PROJECT_ID=$$(gcloud config get-value project) && \
	PROJECT_NUMBER=$$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)") && \
	gcloud run deploy ollama-gemma \
	--project ${PROJECT_ID} \
	--region ${REGION} \
	--source . \
	--port 8080 \
	--cpu 4000m \
	--gpu=1 \
	--gpu-type=nvidia-l4 \
	--no-gpu-zonal-redundancy \
	--memory 16Gi \
	--concurrency 10 \
	--service-account movie-guru-chat-server-sa@${PROJECT_ID}.iam.gserviceaccount.com \
	--startup-probe="initialDelaySeconds=30,tcpSocket.port=8080,timeoutSeconds=240,periodSeconds=240,failureThreshold=1" \
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