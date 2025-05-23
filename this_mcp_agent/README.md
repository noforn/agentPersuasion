# Project Title: MCP Agent - Slack Assistant

## Overview
A Slack bot that integrates with Google Calendar, Kasa smart lights, and travel planning tools (Airbnb, Google Maps) to act as a personal assistant. It monitors a Slack channel for commands and can also answer general questions.

## Features
*   **Google Calendar Integration:** List upcoming events, create new events, and delete existing events.
*   **Kasa Smart Light Control:** Turn lights on/off, adjust brightness, and change light color (HSV).
*   **Slack Communication:** Monitors a specified Slack channel for user requests and sends responses/updates back to the channel.
*   **Travel Planning:**
    *   Search for accommodations using Airbnb.
    *   Get directions and location information using Google Maps.
*   **General Question Answering:** Responds to general queries using its knowledge base and search capabilities.
*   **Proactive Monitoring:** Periodically checks Slack and provides status updates.

## Use Cases
*   "Hey bot, what's on my calendar today?"
*   "Bot, create an event for 'Team Meeting' tomorrow at 10 AM."
*   "Can you turn on the living room lights?"
*   "Set the office lights to blue."
*   "Find me an Airbnb in Paris for next week."
*   "How do I get to the nearest coffee shop?"
*   "What's the weather like today?"

## Setup
*   Ensure Python environment is set up.
*   Install necessary dependencies (e.g., `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`, `python-kasa`, `google-generativeai`, `google-ads-googleads`, `python-dotenv`).
*   Set up environment variables for API keys and tokens:
    *   `GOOGLE_API_KEY`
    *   `GOOGLE_MAPS_API_KEY`
    *   `SLACK_BOT_TOKEN`
    *   `SLACK_TEAM_ID` (replace placeholder `<team_id>`)
    *   `SLACK_CHANNEL_IDS` (replace placeholder `<channel_id>`)
*   Google Calendar API: Requires `credentials.json` and `token.json` (generated after initial OAuth flow).
*   Kasa Lights: Update `FIRST_IP_ADDRESS` and `SECOND_IP_ADDRESS` in `lightTools.py` with your device IPs.

## How to Run
*   Execute the main application script: `python this_mcp_agent/simple-stream.py`
