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

resource "google_compute_network" "custom" {
  name                    = "movie-guru-network"
  auto_create_subnetworks = false
  project                 = var.project_id
  depends_on              = [google_project_service.enable_apis]

}

resource "google_compute_subnetwork" "proxy_subnet" {
  name          = "movieguru-proxy-subnet"
  region        = var.region
  network       = google_compute_network.custom.name
  purpose       = "REGIONAL_MANAGED_PROXY"
  ip_cidr_range = "10.129.0.0/23" # Must be /23 or smaller
  role          = "ACTIVE"
}

resource "google_compute_subnetwork" "producer_subnet" {
  name          = "movieguru-producer-subnet"
  region        = var.region
  network       = google_compute_network.custom.id
  ip_cidr_range = "10.3.0.0/16"
}

resource "google_compute_global_address" "external_ip" {
  name         = "movie-guru-external-ip"
  project      = var.project_id
  address_type = "EXTERNAL"
  ip_version   = "IPV4"
  depends_on   = [google_project_service.enable_apis]
}
