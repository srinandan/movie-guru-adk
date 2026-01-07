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

resource "google_compute_managed_ssl_certificate" "default" {
  name = "${var.app_name}-certificate"
  managed {
    domains = ["${var.app_name}.endpoints.${var.project_id}.cloud.goog"]
  }
}

resource "google_dns_managed_zone" "private-zone" {
  name        = "runapp"
  dns_name    = "run.app."
  description = "Private DNS Zone for Cloud Run"

  visibility = "private"

  private_visibility_config {
    networks {
      network_url = google_compute_network.custom.id
    }
  }
}

resource "google_dns_record_set" "cloudrun" {
  type = "A"
  ttl  = 300

  name = "run.app"

  managed_zone = google_dns_managed_zone.private-zone.name

  rrdatas = ["199.36.153.8", "199.36.153.9", "199.36.153.10", "199.36.153.11"]
}

resource "google_dns_record_set" "cname" {
  name         = "*.run.app"
  managed_zone = google_dns_managed_zone.private-zone.name
  type         = "CNAME"
  ttl          = 300
  rrdatas      = ["run.app."]
}