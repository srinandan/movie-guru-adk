# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

resource "google_cloud_run_v2_job" "db-init" {
  name                = "db-init-job"
  location            = var.region
  project             = var.project_id
  deletion_protection = false
  template {
    template {
      service_account = google_service_account.sa.email
      containers {
        # should be replaced later.
        image = "us-docker.pkg.dev/cloudrun/container/hello:latest"
        name  = "db-init"
        env {
          name = "DB_PASS"
          value_source {
            secret_key_ref {
              secret  = module.secret-manager.secret_names[1]
              version = "latest" # module.secret-manager.secret_versions[0]
            }
          }
        }
        env {
          name  = "DB_HOST"
          value = google_compute_address.cloudsql.address #module.pg.dns_name
        }
        env {
          name  = "DB_NAME"
          value = var.db_name
        }
        env {
          name  = "DB_USER"
          value = "postgres"
        }
        resources {
          limits = {
            cpu    = "2"
            memory = "1024Mi"
          }
        }
      }
      vpc_access {
        egress = "ALL_TRAFFIC"
        network_interfaces {
          network    = google_compute_network.custom.name
          subnetwork = google_compute_subnetwork.custom.name
        }
      }
    }
  }
  lifecycle {
    ignore_changes = [
      launch_stage,
    ]
  }
  depends_on = [module.pg]
}
