# Terraform Infrastructure

This directory contains the Terraform configuration for provisioning the infrastructure required for the Movie Guru application on Google Cloud.

## infrastructure Overview

The Terraform scripts provision the following resources:

*   **Networking**:
    *   A custom VPC network (`movie-guru-network`).
    *   Subnets for application, proxy (Regional Managed Proxy), and producers.
    *   Private Service Connect (PSC) policies for secure connectivity.
    *   Global External IP.
*   **Database**:
    *   Cloud SQL for PostgreSQL 15 (Enterprise Plus).
    *   Regional High Availability configuration.
    *   Private Service Connect (PSC) enabled.
    *   IAM authentication enabled.
    *   Database users and passwords securely stored in Secret Manager.
*   **Caching**:
    *   Memorystore for Redis Cluster.
    *   PSC enabled for private connectivity.
*   **APIs**: Enabling necessary Google Cloud APIs (Vertex AI, Artifact Registry, Run, SQL Admin, etc.).

## Prerequisites

*   [Google Cloud SDK (gcloud)](https://cloud.google.com/sdk/docs/install)
*   Make (optional, for using the Makefile)

## Configuration

The configuration is managed via Terraform variables. Key variables include:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `project_id` | The Google Cloud Project ID. | (Required) |
| `region` | The Google Cloud region for resources. | `us-central1` |
| `app_name` | The application name, used for naming resources. | `movie-guru` |

## Deployment

The deployment is automated using **Cloud Build** running in a private worker pool to ensure secure access to VPC resources.

### 0. Initial Setup

First, create the GCS bucket in your project. This is a one-time setup.

```bash
gcloud config set project ${PROJECT_ID}
gcloud config set compute/region ${REGION}
gcloud auth application-default set-quota-project ${PROJECT_ID}
export REGION=${REGION}
# this GCS bucket will be used for storing the Terraform state
make bucket
```

### 1. Create Private Worker Pool

First, create the private worker pool in your project. This is a one-time setup.

```bash
make worker-pool
```

This command runs `gcloud builds worker-pools create` to set up a private pool named `movie-guru`.

### 2. Deploy Infrastructure

To provision or update the infrastructure, run:

```bash
make backend
```

### 3. Deploy Movies Data

To deploy the movies data, run:

```bash
cd movies-data && make backend && cd ..
```

### 4. Copy the posters to the GCS bucket

```bash
cd movies-posters && gsutil -m cp -r *.png gs://${PROJECT_ID}_posters && cd ..
```

### 5. Enable IAP

To enable IAP, obtain the OAuth2 client ID and secret from the IAP console and run:

```bash
gcloud compute backend-services update movie-guru-chatbot --global --iap=enabled,oauth2-client-id=${OAUTH2_CLIENT_ID},oauth2-client-secret=${OAUTH2_CLIENT_SECRET}
gcloud compute backend-services update movie-guru-agent --global --iap=enabled,oauth2-client-id=${OAUTH2_CLIENT_ID},oauth2-client-secret=${OAUTH2_CLIENT_SECRET}
```

This command submits a Cloud Build job using `dev-infra.yaml`. Key steps performed by the build:
1.  **Init**: Initializes Terraform with a GCS backend (`bucket=${PROJECT_ID}`).
2.  **Apply**: Runs `terraform apply` to create/update resources.


