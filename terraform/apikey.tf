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

resource "google_apikeys_key" "movie-guru-key" {
  name         = "movie-guru-key"
  display_name = "Movie Guru Key"
}

resource "google_secret_manager_secret" "gemini-api-key" {
  name     = "gemini-api-key"
  secret_data = google_apikeys_key.movie-guru-key.key
}

data "google_iam_policy" "secret-manager-policy" {
  binding {
    role = "roles/secretmanager.secretAccessor"
    members = [
      "serviceAccount:${google_service_account.movie-guru-agent.email}",
    ]
  }
}

resource "google_secret_manager_secret_iam_policy" "policy" {
  secret_id = google_secret_manager_secret.gemini-api-key.name
  policy_data = data.google_iam_policy.secret-manager-policy.policy_data
}