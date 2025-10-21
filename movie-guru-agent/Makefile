install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/0.6.12/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync --dev --extra jupyter --frozen

playground:
	@echo "==============================================================================="
	@echo "| 🚀 Starting your agent playground...                                        |"
	@echo "|                                                                             |"
	@echo "| 💡 Try asking: Can you recommend some action movies?                        |"
	@echo "|                                                                             |"
	@echo "| 🔍 IMPORTANT: Select the 'app' folder to interact with your agent.          |"
	@echo "==============================================================================="
	uv run adk web --port 8501

backend:
	PROJECT_ID=$$(gcloud config get-value project) && \
	PROJECT_NUMBER=$$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)") && \
	gcloud run deploy movie-guru-agent \
	--project ${PROJECT_ID} \
	--region ${REGION} \
	--source . \
	--port 8080 \
	--cpu 1000m \
	--memory 1Gi \
	--concurrency 10 \
	--service-account movie-guru-chat-server-sa@${PROJECT_ID}.iam.gserviceaccount.com \
	--set-env-vars MCPTOOLSET_URL="movie-guru-mcp-server-${PROJECT_NUMBER}.${REGION}.run.app,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},MODEL=gemini-2.5-flash,DB_HOST=10.2.0.2,ALLOW_ORIGINS=*,A2A_CONV_AGENT=conversation-analysis-agent-${PROJECT_NUMBER}.${REGION}.run.app" \
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
agent-engine:
	# Export dependencies to requirements file using uv export.
	uv export --no-hashes --no-header --no-dev --no-emit-project --no-annotate --frozen > .requirements.txt 2>/dev/null || \
	uv export --no-hashes --no-header --no-dev --no-emit-project --frozen > .requirements.txt && uv run app/agent_engine_app.py --project=$${PROJECT_ID} --set-env-vars="MCPTOOLSET_URL=movie-guru-mcp-server-$${PROJECT_NUMBER}.us-central1.run.app,MODEL=gemini-2.5-flash,DB_HOST=10.2.0.2"

local-backend:
	uv run uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload

setup-dev-env:
	PROJECT_ID=$$(gcloud config get-value project) && \
	(cd deployment/terraform/dev && terraform init && terraform apply --var-file vars/env.tfvars --var dev_project_id=$$PROJECT_ID --auto-approve)

test:
	uv run pytest tests/unit && uv run pytest tests/integration

lint:
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run mypy .

test-agent-engine:
	VERTEX_RUNTIME=$$(cat deployment_metadata.json | jq -r .remote_agent_engine_id) && \
	(curl -H "Authorization: Bearer $$(gcloud auth print-access-token)" -H "Content-Type: application/json" https://$${REGION}-aiplatform.googleapis.com/v1/$${VERTEX_RUNTIME}:query \
	-d "{\"class_method\": \"create_session\", \"input\": {\"user_id\": \"$${USER}@google.com\"},}" | jq -r .output.id > sessionid.txt) && \
	(curl -N -H "Authorization: Bearer $$(gcloud auth print-access-token)" -H "Content-Type: application/json" https://$${REGION}-aiplatform.googleapis.com/v1/$${VERTEX_RUNTIME}:streamQuery?alt=sse \
	-d "{\"class_method\": \"stream_query\",\"input\": {\"user_id\": \"$${USER}@google.com\",\"session_id\": \"$$(cat sessionid.txt)\",\"message\": \"Can you recommend some action movies?\",}}")

test-run-sse:
	(curl -H "x-goog-authenticated-user-email: $${USER}@google.com" "https://movie-guru-agent-$${PROJECT_NUMBER}.$${REGION}.run.app/sessions" -H "Content-Type: application/json" -d "{\"state\": {\"login\": \"true\"}}" | jq -r .session_id > sessionid.txt) && \
	(curl -N -H "x-goog-authenticated-user-email: $${USER}@google.com" -H "Content-Type: application/json" "https://movie-guru-agent-$${PROJECT_NUMBER}.$${REGION}.run.app/run_sse" -d "{\"appName\": \"app\",\"userId\": \"$${USER}@google.com\",\"sessionId\": \"$$(cat sessionid.txt)\",\"newMessage\": {\"role\": \"user\",\"parts\": [{\"text\": \"Can you recommend a few action movies?\"}]},\"streaming\": false}")