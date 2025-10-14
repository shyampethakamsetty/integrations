# Integrations Platform

A full-stack integration platform that enables OAuth2-based connections to third-party services like Airtable, Notion, and HubSpot. The platform provides a unified interface for authorizing, managing credentials, and fetching data from various integrations.

## 🚀 Features

- **OAuth2 Authentication Flow**: Secure OAuth2 implementation with PKCE for Airtable and standard OAuth2 for Notion
- **Multi-Integration Support**: Currently supports Airtable and Notion, with HubSpot integration in progress
- **Temporary Credential Storage**: Redis-based secure credential caching with automatic expiration
- **React-based UI**: Modern, responsive interface built with Material-UI
- **RESTful API**: FastAPI backend with comprehensive integration endpoints
- **Data Loading**: Fetch and display data from connected integrations (bases, tables, pages, databases)

## 📋 Table of Contents

- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Supported Integrations](#supported-integrations)
- [Development](#development)

## 🏗️ Architecture

The application follows a client-server architecture:

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│                 │         │                  │         │                 │
│  React Frontend │◄───────►│  FastAPI Backend │◄───────►│  Redis Cache    │
│  (Port 3000)    │         │  (Port 8000)     │         │  (Port 6379)    │
│                 │         │                  │         │                 │
└─────────────────┘         └──────────────────┘         └─────────────────┘
                                     │
                                     │ OAuth2
                                     ▼
                    ┌────────────────────────────────┐
                    │  Third-Party Services          │
                    │  - Airtable API                │
                    │  - Notion API                  │
                    │  - HubSpot API (In Progress)   │
                    └────────────────────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Redis**: In-memory data store for temporary credential caching
- **httpx**: Async HTTP client for API requests
- **Python 3.x**: Core programming language

### Frontend
- **React 18.2**: UI library
- **Material-UI (MUI)**: Component library
- **Axios**: HTTP client for API requests
- **React Flow**: Visual workflow representation

### Integration APIs
- Airtable API (OAuth2 with PKCE)
- Notion API (OAuth2)
- HubSpot API (In Development)

## 📁 Project Structure

```
integrations/
├── backend/
│   ├── integrations/
│   │   ├── airtable.py          # Airtable OAuth & data fetching
│   │   ├── notion.py            # Notion OAuth & data fetching
│   │   ├── hubspot.py           # HubSpot integration (TODO)
│   │   └── integration_item.py  # Integration item data model
│   ├── main.py                  # FastAPI application & routes
│   ├── redis_client.py          # Redis client utilities
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── public/                  # Static assets
│   ├── src/
│   │   ├── integrations/
│   │   │   ├── airtable.js     # Airtable integration component
│   │   │   ├── notion.js       # Notion integration component
│   │   │   └── slack.js        # Placeholder for Slack
│   │   ├── App.js              # Main application component
│   │   ├── integration-form.js # Integration selection form
│   │   ├── data-form.js        # Data loading interface
│   │   ├── index.js            # React entry point
│   │   └── index.css           # Global styles
│   ├── package.json            # Node dependencies
│   └── README.md               # Frontend-specific documentation
└── README.md                   # This file
```

## 📦 Prerequisites

- **Python 3.8+**
- **Node.js 16+** and npm
- **Redis Server** (running on localhost:6379 or configured via `REDIS_HOST`)
- **OAuth2 Credentials** for integrations (Airtable, Notion)

## 🔧 Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## ⚙️ Configuration

### Backend Configuration

1. **Redis**: Set the `REDIS_HOST` environment variable if not using localhost:
```bash
export REDIS_HOST=your-redis-host
```

2. **OAuth2 Credentials**: Update the following files with your OAuth2 credentials:

**Airtable** (`backend/integrations/airtable.py`):
```python
CLIENT_ID = 'your-airtable-client-id'
CLIENT_SECRET = 'your-airtable-client-secret'
REDIRECT_URI = 'http://localhost:8000/integrations/airtable/oauth2callback'
```

**Notion** (`backend/integrations/notion.py`):
```python
CLIENT_ID = 'your-notion-client-id'
CLIENT_SECRET = 'your-notion-client-secret'
REDIRECT_URI = 'http://localhost:8000/integrations/notion/oauth2callback'
```

### Frontend Configuration

The frontend is configured to connect to the backend at `http://localhost:8000`. Update the API URLs in the integration files if using a different backend URL.

## 🚀 Running the Application

### Start Redis (if not already running)
```bash
redis-server
```

### Start Backend
```bash
cd backend
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000`

### Start Frontend
```bash
cd frontend
npm start
```
The UI will be available at `http://localhost:3000`

## 📚 API Documentation

### Common Endpoints Pattern

Each integration follows this pattern:

#### 1. Authorization
```
POST /integrations/{integration}/authorize
Body: user_id, org_id (form data)
Response: OAuth2 authorization URL
```

#### 2. OAuth2 Callback
```
GET /integrations/{integration}/oauth2callback
Query Params: code, state
Response: HTML page that closes the OAuth window
```

#### 3. Get Credentials
```
POST /integrations/{integration}/credentials
Body: user_id, org_id (form data)
Response: OAuth2 credentials (access_token, etc.)
```

#### 4. Load Data
```
POST /integrations/{integration}/load
Body: credentials (JSON string in form data)
Response: Array of integration items
```

### Airtable Endpoints

- `POST /integrations/airtable/authorize`
- `GET /integrations/airtable/oauth2callback`
- `POST /integrations/airtable/credentials`
- `POST /integrations/airtable/load` - Fetches bases and tables

### Notion Endpoints

- `POST /integrations/notion/authorize`
- `GET /integrations/notion/oauth2callback`
- `POST /integrations/notion/credentials`
- `POST /integrations/notion/load` - Fetches pages and databases

### HubSpot Endpoints (In Development)

- `POST /integrations/hubspot/authorize`
- `GET /integrations/hubspot/oauth2callback`
- `POST /integrations/hubspot/credentials`
- `POST /integrations/hubspot/get_hubspot_items`

### Health Check
```
GET /
Response: {"Ping": "Pong"}
```

## 🔌 Supported Integrations

### Airtable ✅
- **OAuth2 Flow**: PKCE-enabled OAuth2
- **Data Access**: Fetches all bases and their tables
- **Scopes**: 
  - `data.records:read`, `data.records:write`
  - `data.recordComments:read`, `data.recordComments:write`
  - `schema.bases:read`, `schema.bases:write`

### Notion ✅
- **OAuth2 Flow**: Standard OAuth2
- **Data Access**: Fetches pages and databases accessible to the workspace
- **API Version**: 2022-06-28

### HubSpot 🚧 (In Progress)
- Implementation pending

## 🧑‍💻 Development

### IntegrationItem Data Model

All integrations use the `IntegrationItem` class to represent data:

```python
IntegrationItem(
    id: str,                           # Unique identifier
    type: str,                         # Type (e.g., "Base", "Table", "Page")
    name: str,                         # Display name
    parent_id: Optional[str],          # Parent item ID
    parent_path_or_name: Optional[str], # Parent name/path
    directory: bool,                   # Is directory/container
    creation_time: Optional[datetime],  # Creation timestamp
    last_modified_time: Optional[datetime], # Last modified
    url: Optional[str],                # Item URL
    children: Optional[List[str]],     # Child item IDs
    mime_type: Optional[str],          # MIME type
    visibility: Optional[bool]         # Visibility flag
)
```

### OAuth2 Flow Sequence

1. User initiates connection from frontend
2. Frontend calls `/authorize` endpoint with user and org IDs
3. Backend generates OAuth2 URL and stores state in Redis
4. User authorizes in popup window
5. OAuth provider redirects to `/oauth2callback`
6. Backend exchanges code for tokens
7. Tokens stored in Redis temporarily (10 minutes)
8. Frontend polls for credentials via `/credentials` endpoint
9. Credentials retrieved and cached in frontend
10. Frontend can now load data using stored credentials

### Redis Key Patterns

- State: `{integration}_state:{org_id}:{user_id}`
- Verifier (Airtable PKCE): `airtable_verifier:{org_id}:{user_id}`
- Credentials: `{integration}_credentials:{org_id}:{user_id}`

All keys expire after 600 seconds (10 minutes).

### Adding New Integrations

To add a new integration:

1. Create a new file in `backend/integrations/{integration}.py`
2. Implement the following functions:
   - `authorize_{integration}(user_id, org_id)`
   - `oauth2callback_{integration}(request)`
   - `get_{integration}_credentials(user_id, org_id)`
   - `get_items_{integration}(credentials)`
3. Add routes in `backend/main.py`
4. Create React component in `frontend/src/integrations/{integration}.js`
5. Update `integrationMapping` in `frontend/src/integration-form.js`
6. Update `endpointMapping` in `frontend/src/data-form.js`
