# hubspot.py

import os
from dotenv import load_dotenv
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
load_dotenv()

# HubSpot OAuth2 Configuration
CLIENT_ID = os.getenv('HUBSPOT_CLIENT_ID')
CLIENT_SECRET = os.getenv('HUBSPOT_CLIENT_SECRET')
encoded_client_id_secret = base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()

REDIRECT_URI = os.getenv('BACKEND_BASE_URL') + '/integrations/hubspot/oauth2callback'
authorization_url = f'https://app-na2.hubspot.com/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=crm.schemas.companies.write%20crm.schemas.contacts.write%20crm.schemas.deals.read%20crm.schemas.deals.write%20oauth%20crm.objects.contacts.write%20crm.objects.companies.write%20crm.objects.companies.read%20crm.objects.deals.read%20crm.schemas.contacts.read%20crm.objects.deals.write%20crm.objects.contacts.read%20crm.schemas.companies.read'

async def authorize_hubspot(user_id, org_id):
    state_data = {
        'state': secrets.token_urlsafe(32),
        'user_id': user_id,
        'org_id': org_id
    }
    encoded_state = json.dumps(state_data)
    await add_key_value_redis(f'hubspot_state:{org_id}:{user_id}', encoded_state, expire=600)

    return f'{authorization_url}&state={encoded_state}'

async def oauth2callback_hubspot(request: Request):
    if request.query_params.get('error'):
        raise HTTPException(status_code=400, detail=request.query_params.get('error'))
    code = request.query_params.get('code')
    encoded_state = request.query_params.get('state')
    state_data = json.loads(encoded_state)

    original_state = state_data.get('state')
    user_id = state_data.get('user_id')
    org_id = state_data.get('org_id')

    saved_state = await get_value_redis(f'hubspot_state:{org_id}:{user_id}')

    if not saved_state or original_state != json.loads(saved_state).get('state'):
        raise HTTPException(status_code=400, detail='State does not match.')

    async with httpx.AsyncClient() as client:
        response, _ = await asyncio.gather(
            client.post(
                'https://api.hubapi.com/oauth/v1/token',
                data={
                    'grant_type': 'authorization_code',
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                    'redirect_uri': REDIRECT_URI,
                    'code': code
                },
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
            ),
            delete_key_redis(f'hubspot_state:{org_id}:{user_id}'),
        )

    await add_key_value_redis(f'hubspot_credentials:{org_id}:{user_id}', json.dumps(response.json()), expire=600)
    
    close_window_script = """
    <html>
        <script>
            window.close();
        </script>
    </html>
    """
    return HTMLResponse(content=close_window_script)

async def get_hubspot_credentials(user_id, org_id):
    credentials = await get_value_redis(f'hubspot_credentials:{org_id}:{user_id}')
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    credentials = json.loads(credentials)
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    await delete_key_redis(f'hubspot_credentials:{org_id}:{user_id}')

    return credentials

def create_integration_item_metadata_object(
    response_json: dict, item_type: str, parent_id=None, parent_name=None
) -> IntegrationItem:
    """Creates an integration metadata object from HubSpot API response"""
    integration_item_metadata = IntegrationItem(
        id=response_json.get('id', ''),
        name=response_json.get('name', response_json.get('title', response_json.get('properties', {}).get('name', 'Unnamed'))),
        type=item_type,
        parent_id=parent_id,
        parent_path_or_name=parent_name,
        url=response_json.get('url', ''),
        creation_time=response_json.get('createdAt', response_json.get('created', None)),
        last_modified_time=response_json.get('updatedAt', response_json.get('updated', None)),
    )

    return integration_item_metadata

async def get_items_hubspot(credentials) -> list[IntegrationItem]:
    """Aggregates all metadata relevant for a HubSpot integration"""
    credentials = json.loads(credentials)
    access_token = credentials.get('access_token')
    
    if not access_token:
        raise HTTPException(status_code=400, detail='No access token found in credentials.')
    
    list_of_integration_item_metadata = []
    
    # Get contacts
    contacts_response = requests.get(
        'https://api.hubapi.com/crm/v3/objects/contacts',
        headers={'Authorization': f'Bearer {access_token}'},
        params={'limit': 100, 'properties': 'firstname,lastname,email,createdate,lastmodifieddate'}
    )
    
    if contacts_response.status_code == 200:
        contacts_data = contacts_response.json()
        for contact in contacts_data.get('results', []):
            # Create a name from firstname and lastname
            first_name = contact.get('properties', {}).get('firstname', '')
            last_name = contact.get('properties', {}).get('lastname', '')
            contact_name = f"{first_name} {last_name}".strip() or contact.get('id', 'Unnamed Contact')
            
            contact['name'] = contact_name
            list_of_integration_item_metadata.append(
                create_integration_item_metadata_object(
                    contact, 
                    'Contact',
                    parent_id='crm',
                    parent_name='HubSpot CRM'
                )
            )
    
    # Get companies
    companies_response = requests.get(
        'https://api.hubapi.com/crm/v3/objects/companies',
        headers={'Authorization': f'Bearer {access_token}'},
        params={'limit': 100, 'properties': 'name,createdate,lastmodifieddate'}
    )
    
    if companies_response.status_code == 200:
        companies_data = companies_response.json()
        for company in companies_data.get('results', []):
            company['name'] = company.get('properties', {}).get('name', company.get('id', 'Unnamed Company'))
            list_of_integration_item_metadata.append(
                create_integration_item_metadata_object(
                    company, 
                    'Company',
                    parent_id='crm',
                    parent_name='HubSpot CRM'
                )
            )
    
    # Get deals
    deals_response = requests.get(
        'https://api.hubapi.com/crm/v3/objects/deals',
        headers={'Authorization': f'Bearer {access_token}'},
        params={'limit': 100, 'properties': 'dealname,amount,closedate,createdate,lastmodifieddate'}
    )
    
    if deals_response.status_code == 200:
        deals_data = deals_response.json()
        for deal in deals_data.get('results', []):
            deal['name'] = deal.get('properties', {}).get('dealname', deal.get('id', 'Unnamed Deal'))
            list_of_integration_item_metadata.append(
                create_integration_item_metadata_object(
                    deal, 
                    'Deal',
                    parent_id='crm',
                    parent_name='HubSpot CRM'
                )
            )
    
    # REMOVED: Workflows section since we don't have automation scope
    
    # Get blog posts (using cms.performance.read scope)
    blog_posts_response = requests.get(
        'https://api.hubapi.com/cms/v3/blogs/posts',
        headers={'Authorization': f'Bearer {access_token}'},
        params={'limit': 100, 'state': 'PUBLISHED'}
    )
    
    if blog_posts_response.status_code == 200:
        blog_posts_data = blog_posts_response.json()
        for post in blog_posts_data.get('results', []):
            list_of_integration_item_metadata.append(
                create_integration_item_metadata_object(
                    post, 
                    'Blog Post',
                    parent_id='content',
                    parent_name='HubSpot Content'
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
    
    print(f'HubSpot integration items: {serialized_items}')
    return serialized_items