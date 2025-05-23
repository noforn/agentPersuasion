# MCP Agent Testing

## Overview
An Agent that integrates with Google Calendar, Kasa smart lights, and travel planning tools (Airbnb, Google Maps) to act as a personal assistant. It monitors a Slack channel for user input.

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
*   "Hey Agent, what's on my calendar today?"
*   "@Agent, create an event for 'Team Meeting' tomorrow at 10 AM."
*   "Can you turn on the living room lights?"
*   "Set the office lights to blue."
*   "Find me an Airbnb in Paris for next week."
*   "How do I get to the nearest coffee shop?"
*   "What's the weather like today?"

## Setup
```python
uv venv --python 3.11
source venv/bin/activate
uv pip install -r requirements.txt
mv .env-exp .env
```
*   Set up environment variables for API keys and tokens:
    *   `GOOGLE_API_KEY`
    *   `GOOGLE_MAPS_API_KEY`
    *   `SLACK_BOT_TOKEN`
    *   `SLACK_TEAM_ID` (replace placeholders `<team_id>`)
    *   `SLACK_CHANNEL_IDS` (replace placeholders `<channel_id>`)
*   Google Calendar API: Requires `credentials.json` and `token.json` (generated after initial OAuth flow).
*   Kasa Lights: Update `FIRST_IP_ADDRESS` and `SECOND_IP_ADDRESS` in `lightTools.py` with your device IPs.

## Usage
```python
python this_mcp_agent/simple-stream.py
```
