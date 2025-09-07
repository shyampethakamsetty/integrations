import { useState } from 'react';
import {
    Box,
    Autocomplete,
    TextField,
    Button,
} from '@mui/material';
import { AirtableIntegration } from './integrations/airtable';
import { NotionIntegration } from './integrations/notion';
import { SlackIntegration } from './integrations/slack';
import { HubspotIntegration } from './integrations/hubspot';
import { DataForm } from './data-form';

const integrationMapping = {
    'Notion': NotionIntegration,
    'Airtable': AirtableIntegration,
    'Slack': SlackIntegration,
    'Hubspot': HubspotIntegration,
};

export const IntegrationForm = () => {
    const [integrationParams, setIntegrationParams] = useState({});
    const [user, setUser] = useState('TestUser');
    const [org, setOrg] = useState('TestOrg');
    const [currType, setCurrType] = useState(null);
    const CurrIntegration = integrationMapping[currType];

  return (
    <Box display='flex' justifyContent='center' alignItems='center' flexDirection='column' sx={{ width: '100%' }}>
        <Box display='flex' flexDirection='column'>
        <TextField
            label="User"
            value={user}
            onChange={(e) => setUser(e.target.value)}
            sx={{mt: 2}}
        />
        <TextField
            label="Organization"
            value={org}
            onChange={(e) => setOrg(e.target.value)}
            sx={{mt: 2}}
        />
        <Autocomplete
            id="integration-type"
            options={Object.keys(integrationMapping)}
            sx={{ width: 300, mt: 2 }}
            renderInput={(params) => <TextField {...params} label="Integration Type" />}
            onChange={(e, value) => setCurrType(value)}
        />
        </Box>
        {currType && 
        <Box>
            <CurrIntegration user={user} org={org} integrationParams={integrationParams} setIntegrationParams={setIntegrationParams} />
        </Box>
        }
        {integrationParams?.credentials &&
  <Box sx={{ mt: 2 }} display="flex" gap={2} alignItems="center">
    <DataForm integrationType={integrationParams?.type} credentials={integrationParams?.credentials} />
    <Button
      variant="outlined"
      color="warning"
      onClick={() => setIntegrationParams({})}
    >
      Reset connection
    </Button>
  </Box>
}
    </Box>
  );
}
