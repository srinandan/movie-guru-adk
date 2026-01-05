PROJECT_ID ?= $(shell gcloud config get-value project)
PROJECT_NUMBER ?= $(shell gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")
REGION ?= us-central1
_COMMIT_SHA ?= $(shell echo | find *.py pyproject.toml uv.lock -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -c 1-10)

.PHONY: backend local-backend

backend:
	export _COMMIT_SHA=${_COMMIT_SHA} ;\
	export REGION=${REGION} ;\
	export PROJECT_ID=${PROJECT_ID} ;\
	export PROJECT_NUMBER=${PROJECT_NUMBER} ;\
	gcloud builds submit --config=deployment/cd/dev-cloudrun.yaml --region=${REGION} --substitutions=_COMMIT_SHA=${_COMMIT_SHA},_REGION=${REGION}

local-backend:
	uv run .

lint:
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format .
	uv run mypy .