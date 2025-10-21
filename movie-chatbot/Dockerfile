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

# Use an official Node.js runtime as a parent image
FROM node:22-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json index.html *.js ./

# Install any needed packages
RUN npm install

# Bundle app source
COPY . .

# Build the Vue.js application
RUN npm run build

# Make port 8080 available to the world outside this container
EXPOSE 8080

ENV OTEL_SERVICE_NAME=movie-chatbot
ENV OTEL_TRACES_EXPORTER=otlp
ENV OTEL_EXPORTER_OTLP_ENDPOINT=https://telemetry.googleapis.com
ENV VITE_OTLP_EXPORTER_URL=https://telemetry.googleapis.com

# Run the app when the container launches
CMD ["npm", "start"]