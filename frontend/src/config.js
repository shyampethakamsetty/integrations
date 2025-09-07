// configuration file for the frontend

const config = {

    BASE_URL: process.env.REACT_APP_BASE_URL,
    APP_NAME: process.env.REACT_APP_APP_NAME,

    ENDPOINTS: {
        AIRTABLE: {
            AUTHORIZE: '/integrations/airtable/authorize',
            OAUTH_CALLBACK: '/integrations/airtable/oauth2callback',
            CREDENTIALS: '/integrations/airtable/credentials',
            LOAD: '/integrations/airtable/load',
        },
        NOTION: {
            AUTHORIZE: '/integrations/notion/authorize',
            OAUTH_CALLBACK: '/integrations/notion/oauth2callback',
            CREDENTIALS: '/integrations/notion/credentials',
            LOAD: '/integrations/notion/load',
        },
        SLACK: {
            AUTHORIZE: '/integrations/slack/authorize',
            OAUTH_CALLBACK: '/integrations/slack/oauth2callback',
            CREDENTIALS: '/integrations/slack/credentials',
            LOAD: '/integrations/slack/load',
        },
        HUBSPOT: {
            AUTHORIZE: '/integrations/hubspot/authorize',
            OAUTH_CALLBACK: '/integrations/hubspot/oauth2callback',
            CREDENTIALS: '/integrations/hubspot/credentials',
            LOAD: '/integrations/hubspot/load',
        }
    }
}

export default config;