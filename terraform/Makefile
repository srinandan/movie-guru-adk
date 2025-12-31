PROJECT_ID ?= $(shell gcloud config get-value project)
PROJECT_NUMBER ?= $(shell gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")
REGION ?= us-central1
_COMMIT_SHA ?= $(shell echo | sha256sum | cut -c 1-10)

.PHONY: backend

worker-pool:
	export _COMMIT_SHA=${_COMMIT_SHA} ;\
	export REGION=${REGION} ;\
	export PROJECT_ID=${PROJECT_ID} ;\
	export PROJECT_NUMBER=${PROJECT_NUMBER} ;\
	gcloud builds worker-pools create movie-guru --region=${REGION} --worker-machine-type=e2-standard-16 --worker-disk-size=300 --project=${PROJECT_ID}

backend:
	export _COMMIT_SHA=${_COMMIT_SHA} ;\
	export REGION=${REGION} ;\
	export PROJECT_ID=${PROJECT_ID} ;\
	export PROJECT_NUMBER=${PROJECT_NUMBER} ;\
	gcloud builds submit --config=dev-infra.yaml --region=${REGION} --substitutions=_COMMIT_SHA=${_COMMIT_SHA},_REGION=${REGION}
	