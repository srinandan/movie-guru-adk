PROJECT_ID ?= $(shell gcloud config get-value project)
PROJECT_NUMBER ?= $(shell gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")
REGION ?= us-central1
_COMMIT_SHA ?= $(shell echo | find src public *.js *.html -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -c 1-10)
SERVICE_NAME = movie-chatbot

.PHONY: build docker

docker:
	export _COMMIT_SHA=${_COMMIT_SHA} ;\
	export REGION=${REGION} ;\
	export PROJECT_ID=${PROJECT_ID} ;\
	export PROJECT_NUMBER=${PROJECT_NUMBER} ;\
	docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/movie-guru/movie-chatbot:${_COMMIT_SHA} . ;\
	docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/movie-guru/movie-chatbot:${_COMMIT_SHA}	

backend:
	export _COMMIT_SHA=${_COMMIT_SHA} ;\
	export REGION=${REGION} ;\
	export PROJECT_ID=${PROJECT_ID} ;\
	export PROJECT_NUMBER=${PROJECT_NUMBER} ;\	
	gcloud builds submit --config=deployment/cd/dev-cloudrun.yaml --region=${REGION} --substitutions=_COMMIT_SHA=${_COMMIT_SHA},_REGION=${REGION}