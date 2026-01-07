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

resource "google_compute_url_map" "urlmap" {
  name        = "movie-guru-lb"
  description = "Movie Guru Load Balancer"
  default_service = module.lb-http.backend_services.default.id
  host_rule {
    hosts        = ["*"]
    path_matcher = "allpaths"
  }
  path_matcher {
    name            = "allpaths"
    default_service = module.lb-http.backend_services.default.id
    path_rule {
      paths   = ["/sessions"]
      service = module.lb-http.backend_services.movie-guru-agent.id
    }
    path_rule {
      paths   = ["/random"]
      service = module.lb-http.backend_services.movie-guru-agent.id
    }
    path_rule {
      paths   = ["/sessions/*"]
      service = module.lb-http.backend_services.movie-guru-agent.id
    }
    path_rule {
      paths   = ["/run"]
      service = module.lb-http.backend_services.movie-guru-agent.id
    }    
  }
}

module "lb-http" {
  source  = "terraform-google-modules/lb-http/google//modules/serverless_negs"
  version = "~> 14.0"
  name    = "movie-guru-lb"
  project = var.project_id
  load_balancing_scheme = "EXTERNAL_MANAGED"
  backends = {
    default = {
      description = null
      groups = [
        {
          group = google_compute_region_network_endpoint_group.movie_guru_chatbot_serverless_neg.id
        }
      ]
      enable_cdn = false
      iap_config = {
        enable = false
      }
      log_config = {
        enable = false
      }
    }
    movie-guru-agent = {
      description = null
      groups = [
        {
          group = google_compute_region_network_endpoint_group.movie_guru_agent_serverless_neg.id
        }
      ]
      enable_cdn = false
      iap_config = {
        enable = false
      }
      log_config = {
        enable = false
      }
    }
    movie-guru-chatbot = {
      description = null
      groups = [
        {
          group = google_compute_region_network_endpoint_group.movie_guru_chatbot_serverless_neg.id
        }
      ]
      enable_cdn = false
      iap_config = {
        enable = false
      }
      log_config = {
        enable = false
      }
    }
  }
  create_url_map = false
  url_map        = google_compute_url_map.urlmap.name
  ssl                       = true
  create_ssl_certificate    = false
  random_certificate_suffix = false
  http_forward              = false
  ssl_certificates = [
    google_compute_managed_ssl_certificate.default.id
  ]
}

resource "google_compute_region_network_endpoint_group" "movie_guru_agent_serverless_neg" {
  provider              = google-beta
  name                  = "movie-guru-agent"
  network_endpoint_type = "SERVERLESS"
  region                = var.region
  project               = var.project_id
  cloud_run {
    service = module.cloud_run_movie_guru_agent.service_name
  }
}

resource "google_compute_region_network_endpoint_group" "movie_guru_chatbot_serverless_neg" {
  provider              = google-beta
  name                  = "movie-guru-chatbot"
  network_endpoint_type = "SERVERLESS"
  project               = var.project_id
  region                = var.region
  cloud_run {
    service = module.cloud_run_movie_guru_chatbot.service_name
  }
}