# slack.py

import os
import dotenv
import json
import secrets
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx
import asyncio
import base64
import requests
from integrations.integration_item import IntegrationItem

from redis_client import add_key_value_redis, get_value_redis, delete_key_redis

# load environment variables
dotenv.load_dotenv()

# Slack OAuth2 Configuration
CLIENT_ID = os.getenv('SLACK_CLIENT_ID')
CLIENT_SECRET = os.getenv('SLACK_CLIENT_SECRET')
encoded_client_id_secret = base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()

# Use cloud redirect URL (e.g., Vercel function) to provide a stable HTTPS callback.
# That function should 302-redirect to the local backend callback at
# http://localhost:8000/integrations/slack/oauth2callback with the original query params.
REDIRECT_URI = os.getenv('SLACK_OAUTH_REDIRECT_URL', 'http://localhost:8000/integrations/slack/oauth2callback')
authorization_url = f'https://slack.com/oauth/v2/authorize?client_id={CLIENT_ID}&scope=channels:read,groups:read,im:read,mpim:read,users:read,team:read&user_scope=&redirect_uri={REDIRECT_URI}'

async def authorize_slack(user_id, org_id):
    state_data = {
        'state': secrets.token_urlsafe(32),
        'user_id': user_id,
        'org_id': org_id
    }
    encoded_state = json.dumps(state_data)
    await add_key_value_redis(f'slack_state:{org_id}:{user_id}', encoded_state, expire=600)

    return f'{authorization_url}&state={encoded_state}'

async def oauth2callback_slack(request: Request):
    if request.query_params.get('error'):
        raise HTTPException(status_code=400, detail=request.query_params.get('error'))
    code = request.query_params.get('code')
    encoded_state = request.query_params.get('state')
    state_data = json.loads(encoded_state)

    original_state = state_data.get('state')
    user_id = state_data.get('user_id')
    org_id = state_data.get('org_id')

    saved_state = await get_value_redis(f'slack_state:{org_id}:{user_id}')

    if not saved_state or original_state != json.loads(saved_state).get('state'):
        raise HTTPException(status_code=400, detail='State does not match.')

    async with httpx.AsyncClient() as client:
        response, _ = await asyncio.gather(
            client.post(
                'https://slack.com/api/oauth.v2.access',
                data={
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                    'code': code,
                    # Must match the authorize redirect exactly (cloud URL)
                    'redirect_uri': REDIRECT_URI
                },
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
            ),
            delete_key_redis(f'slack_state:{org_id}:{user_id}')
        )

    await add_key_value_redis(f'slack_credentials:{org_id}:{user_id}', json.dumps(response.json()), expire=600)
    
    close_window_script = """
    <html>
        <script>
            window.close();
        </script>
    </html>
    """
    return HTMLResponse(content=close_window_script)

async def get_slack_credentials(user_id, org_id):
    credentials = await get_value_redis(f'slack_credentials:{org_id}:{user_id}')
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    credentials = json.loads(credentials)
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    await delete_key_redis(f'slack_credentials:{org_id}:{user_id}')

    return credentials

def create_integration_item_metadata_object(
    response_json: dict, item_type: str, parent_id=None, parent_name=None
) -> IntegrationItem:
    """Creates an integration metadata object from Slack API response"""
    integration_item_metadata = IntegrationItem(
        id=response_json.get('id', ''),
        name=response_json.get('name', response_json.get('title', 'Unnamed')),
        type=item_type,
        parent_id=parent_id,
        parent_path_or_name=parent_name,
        url=response_json.get('url', ''),
        creation_time=response_json.get('created', None),
        last_modified_time=response_json.get('updated', None),
    )

    return integration_item_metadata

async def get_items_slack(credentials) -> list[IntegrationItem]:
    """Aggregates all metadata relevant for a Slack integration"""
    credentials = json.loads(credentials)
    access_token = credentials.get('access_token')
    
    if not access_token:
        raise HTTPException(status_code=400, detail='No access token found in credentials.')
    
    list_of_integration_item_metadata = []
    
    # Get channels
    channels_response = requests.get(
        'https://slack.com/api/conversations.list',
        headers={'Authorization': f'Bearer {access_token}'},
        params={'types': 'public_channel,private_channel', 'limit': 1000}
    )
    
    if channels_response.status_code == 200:
        channels_data = channels_response.json()
        if channels_data.get('ok'):
            for channel in channels_data.get('channels', []):
                list_of_integration_item_metadata.append(
                    create_integration_item_metadata_object(
                        channel, 
                        'Channel',
                        parent_id='workspace',
                        parent_name='Slack Workspace'
                    )
                )
    
    # Get direct messages
    dms_response = requests.get(
        'https://slack.com/api/conversations.list',
        headers={'Authorization': f'Bearer {access_token}'},
        params={'types': 'im', 'limit': 1000}
    )
    
    if dms_response.status_code == 200:
        dms_data = dms_response.json()
        if dms_data.get('ok'):
            for dm in dms_data.get('channels', []):
                list_of_integration_item_metadata.append(
                    create_integration_item_metadata_object(
                        dm, 
                        'Direct Message',
                        parent_id='workspace',
                        parent_name='Slack Workspace'
                    )
                )
    
    # Get team info
    team_response = requests.get(
        'https://slack.com/api/team.info',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    if team_response.status_code == 200:
        team_data = team_response.json()
        if team_data.get('ok'):
            team_info = team_data.get('team', {})
            list_of_integration_item_metadata.append(
                create_integration_item_metadata_object(
                    team_info, 
                    'Workspace',
                    parent_id=None,
                    parent_name=None
                )
            )
    
    # Convert IntegrationItem objects to dictionaries for JSON serialization
    serialized_items = []
    for item in list_of_integration_item_metadata:
        item_dict = {
            'id': item.id,
            'type': item.type,
            'directory': item.directory,
            'parent_path_or_name': item.parent_path_or_name,
            'name': item.name,
            'creation_time': item.creation_time,
            'last_modified_time': item.last_modified_time,
            'parent_id': item.parent_id,
            'url': item.url,
            'children': item.children,
            'mime_type': item.mime_type,
            'delta': item.delta,
            'drive_id': item.drive_id,
            'visibility': item.visibility,
        }
        serialized_items.append(item_dict)
    
    print(f'Slack integration items: {serialized_items}')
    return serialized_items

