PROJECT_ID ?= $(shell gcloud config get-value project)
PROJECT_NUMBER ?= $(shell gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")
REGION ?= us-central1
_COMMIT_SHA ?= $(shell echo | sha256sum | cut -c 1-10)

install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/0.6.12/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync --dev --extra jupyter --frozen

backend:
	export _COMMIT_SHA=${_COMMIT_SHA} ;\
	export REGION=${REGION} ;\
	export PROJECT_ID=${PROJECT_ID} ;\
	export PROJECT_NUMBER=${PROJECT_NUMBER} ;\
	gcloud builds submit \
		--config=./deployment/cd/dev-cloudrun.yaml \
		--project ${PROJECT_ID} \
		--region=${REGION} --substitutions=_COMMIT_SHA=${_COMMIT_SHA},_REGION=${REGION}

local-backend:
	uv run app.server:app --host 0.0.0.0 --port 8080 --reload

docker:
	export _COMMIT_SHA=${_COMMIT_SHA} ;\
	export REGION=${REGION} ;\
	export PROJECT_ID=${PROJECT_ID} ;\
	export PROJECT_NUMBER=${PROJECT_NUMBER} ;\
	docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/movie-guru/movie-guru-mcp-server:${_COMMIT_SHA} . ;\
	docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/movie-guru/movie-guru-mcp-server:${_COMMIT_SHA}

lint:
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run mypy .	