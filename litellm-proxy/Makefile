PROJECT_ID ?= $(shell gcloud config get-value project)
PROJECT_NUMBER ?= $(shell gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")
REGION ?= us-central1
_COMMIT_SHA ?= $(shell echo | sha256sum | cut -c 1-10)
pwd := $(shell pwd)

local:
	export _COMMIT_SHA=${_COMMIT_SHA} ;\
	export REGION=${REGION} ;\
	export PROJECT_ID=${PROJECT_ID} ;\
	export PROJECT_NUMBER=${PROJECT_NUMBER} ;\
	docker build -t litellm-proxy:${_COMMIT_SHA} . ;\
	docker run -it --rm --name litellm-proxy \
	-v ${pwd}/local_config.yaml:/app/config.yaml \
	-e GEMINI_API_KEY=${GEMINI_API_KEY} \
	-e VERTEXAI_PROJECT=${PROJECT_ID} \
	-e VERTEXAI_LOCATION=${REGION} \
   	-p 4000:4000 \
   	litellm-proxy:${_COMMIT_SHA} \
	--config /app/config.yaml --detailed_debug

backend:
	export _COMMIT_SHA=${_COMMIT_SHA} ;\
	export REGION=${REGION} ;\
	export PROJECT_ID=${PROJECT_ID} ;\
	export PROJECT_NUMBER=${PROJECT_NUMBER} ;\
	gcloud builds submit --config=deployment/cd/dev-cloudrun.yaml --region=${REGION} --substitutions=_COMMIT_SHA=${_COMMIT_SHA},_REGION=${REGION}