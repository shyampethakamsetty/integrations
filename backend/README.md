# VectorShift Integrations Backend

FastAPI backend for OAuth integrations (Airtable, Notion, Slack, HubSpot). Uses Redis for short‑lived OAuth state and credentials handoff to the frontend.

## Requirements
- Python 3.11+
- Redis server (localhost:6379 by default)
- The corresponding integration apps configured with the correct redirect URIs

## Setup

1) Create and activate a virtual environment

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

2) Install dependencies (uv or pip)

```bash
# Using uv (recommended)
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

3) Configure environment variables

Create a `.env` file in `backend/` (do not commit it). Example:

```env
# environment variables for the backend
REDIS_HOST=localhost

# Airtable
AIRTABLE_CLIENT_ID=your_airtable_client_id
AIRTABLE_CLIENT_SECRET=your_airtable_client_secret

# Notion
NOTION_CLIENT_ID=your_notion_client_id
NOTION_CLIENT_SECRET=your_notion_client_secret

# Slack
SLACK_CLIENT_ID=your_slack_client_id
SLACK_CLIENT_SECRET=your_slack_client_secret
# Vercel redirect URL for Slack (deploy slack-oauth-redirect project first)
SLACK_OAUTH_REDIRECT_URL=https://slack-oauth-redirect/api/slack_oauth_redirect

# HubSpot
HUBSPOT_CLIENT_ID=your_hubspot_client_id
HUBSPOT_CLIENT_SECRET=your_hubspot_client_secret
```