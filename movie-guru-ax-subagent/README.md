# Movie Guru Analytics Sub-agent

This directory contains an ADK-based agent-to-agent (A2A) sub-agent responsible for analyzing conversation sentiment and generating customer satisfaction metrics.

## Overview

The primary function of this sub-agent is to provide conversational analytics. It is designed to be called by other agents (such as the main `movie-guru-agent`) to process a conversation history.

It analyzes the text to determine the overall sentiment (e.g., positive, negative, neutral) and generates a structured metric, such as a customer satisfaction score. This allows the system to gain insights into the quality of user interactions.

## Usage

This agent exposes an A2A endpoint. A parent agent can call this endpoint, passing a user's conversation history as input. The analytics sub-agent will then process the data and return a JSON object containing the sentiment analysis and a calculated customer metric.

This component is not intended to be run as a standalone service for end-users but rather as a specialized microservice within the larger multi-agent system.
