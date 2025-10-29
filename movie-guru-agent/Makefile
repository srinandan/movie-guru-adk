agent-engine:
	# Export dependencies to requirements file using uv export.
	uv export --no-hashes --no-header --no-dev --no-emit-project --no-annotate --frozen > .requirements.txt 2>/dev/null || \
	uv export --no-hashes --no-header --no-dev --no-emit-project --frozen > .requirements.txt && uv run app/agent_engine_app.py --project=$${PROJECT_ID} --set-env-vars="MCPTOOLSET_URL=movie-guru-mcp-server-$${PROJECT_NUMBER}.us-central1.run.app,MODEL=gemini-2.5-flash,DB_HOST=10.2.0.2,A2A_CONV_AGENT=$${REGION-aiplatform.googleapis.com/v1beta1/projects/$${PROJECT_ID}/locations/$${REGION/reasoningEngines/6699794939015856128/a2a"

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