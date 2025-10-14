install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/0.6.12/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync --dev --extra jupyter --frozen

backend:
	PROJECT_ID=$(gcloud config get-value project) && \
	gcloud builds submit \
		--config=./deployment/cd/dev-cloudrun.yaml \
		--project ${PROJECT_ID} \
		--region ${REGION} \
		--worker-pool="projects/${PROJECT_ID}/locations/${REGION}/workerPools/movie-guru"
		--substitutions=_SHORT_SHA=$(git rev-parse HEAD)

local-backend:
	uv run app.server:app --host 0.0.0.0 --port 8080 --reload

lint:
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run mypy .	