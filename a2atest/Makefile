PROJECT_ID ?= $(shell gcloud config get-value project)
PROJECT_NUMBER ?= $(shell gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")
REGION ?= us-central1


recommend-movies:
	@echo "Recommend movies"
	uv run recommend-movies.py

conversation:
	@echo "Conversation Analysis"
	uv run conv-analysis.py