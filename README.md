Full-stack demo app showcasing OAuth connections and metadata fetch for Airtable, Notion, Slack, and HubSpot.

- Backend: FastAPI (OAuth flows, Redis for short‑lived state/credentials, metadata aggregation)
- Frontend: React + MUI (connect flows, load and display items)

## Project structure
```
integrations_technical_assessment/
  backend/           # FastAPI app, integrations, Redis client
  frontend/          # React app
  .gitignore         # Root ignore (frontend + backend)
```

## Prerequisites
- Python 3.11+
- Node.js 18+
- Redis server (localhost:6379 by default)

## Quick start

### 1) Backend
See `backend/README.md` for full details. Summary:
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt  # or: pip install -r requirements.txt

# Create backend/.env (example)
cat > .env <<'EOF'
REDIS_HOST=localhost

AIRTABLE_CLIENT_ID=your_airtable_client_id
AIRTABLE_CLIENT_SECRET=your_airtable_client_secret

NOTION_CLIENT_ID=your_notion_client_id
NOTION_CLIENT_SECRET=your_notion_client_secret

SLACK_CLIENT_ID=your_slack_client_id
SLACK_CLIENT_SECRET=your_slack_client_secret
# Vercel redirect URL for Slack (deploy slack-oauth-redirect project first)
SLACK_OAUTH_REDIRECT_URL=https://slack-oauth-redirect.app/api/slack_oauth_redirect

HUBSPOT_CLIENT_ID=your_hubspot_client_id
HUBSPOT_CLIENT_SECRET=your_hubspot_client_secret
EOF

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
API base URL: `http://localhost:8000`

### 2) Frontend
```bash
cd frontend
# Create .env
cat > .env <<'EOF'
REACT_APP_BASE_URL=http://localhost:8000
REACT_APP_APP_NAME=VectorShift Integrations
EOF

npm install
npm start
```
Frontend runs at `http://localhost:3000`.

## OAuth redirect URIs
Configure these in provider dashboards:
- Airtable: `http://localhost:8000/integrations/airtable/oauth2callback`
- Notion: `http://localhost:8000/integrations/notion/oauth2callback`
- Slack: `https://slack-oauth-redirect.app/api/slack_oauth_redirect` (Vercel function)
- HubSpot: `http://localhost:8000/integrations/hubspot/oauth2callback`

**Note:** Slack uses a Vercel redirect function for stable HTTPS callback. Deploy the `slack-oauth-redirect` project first.

### HubSpot scopes helper
Use scopes that match your account/app. The code builds the authorize URL in `backend/integrations/hubspot.py`.

<img width="809" height="599" alt="HubSpot scopes example" src="https://github.com/user-attachments/assets/717229e6-e065-4bf9-bb8e-89133207ce93" />

## How it works (high level)
- Connect: Frontend requests an authorize URL; backend saves a CSRF `state` to Redis and returns the provider URL.
- Callback: Provider redirects to backend; backend verifies state, exchanges code for tokens, stores credentials briefly in Redis.
- Handoff: Frontend polls `/credentials` to retrieve the credentials (then backend deletes them).
- Load Data: Frontend posts credentials to `/load`; backend calls provider APIs and returns normalized items.

Redis usage keys:
- `<service>_state:{org_id}:{user_id}` (TTL ~10m)
- `<service>_credentials:{org_id}:{user_id}` (TTL ~10m; deleted when read)
