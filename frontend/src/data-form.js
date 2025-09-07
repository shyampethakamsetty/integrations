import { useState } from 'react';
import {
    Box,
    Button,
    Typography,
    Chip,
    Card,
    CardContent
} from '@mui/material';
import axios from 'axios';
import config from './config';

const endpointMapping = {
    'Notion': 'NOTION',
    'Airtable': 'AIRTABLE',
    'HubSpot': 'HUBSPOT',  // Fixed: was 'Hubspot'
    'Slack': 'SLACK',
};

export const DataForm = ({ integrationType, credentials }) => {
    const [loadedData, setLoadedData] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const endpoint = endpointMapping[integrationType];

    const handleLoad = async () => {
        try {
            setIsLoading(true);
            const formData = new FormData();
            formData.append('credentials', JSON.stringify(credentials));
            const response = await axios.post(`${config.BASE_URL}${config.ENDPOINTS[endpoint].LOAD}`, formData);
            const data = response.data;
            setLoadedData(data);
        } catch (e) {
            alert(e?.response?.data?.detail);
        } finally {
            setIsLoading(false);
        }
    }

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        return new Date(dateString).toLocaleString();
    }

    const getTypeColor = (type) => {
        switch (type) {
            case 'database': return 'primary';
            case 'page': return 'secondary';
            default: return 'default';
        }
    }

    return (
        <Box display='flex' justifyContent='center' alignItems='center' flexDirection='column' width='100%'>
            <Box display='flex' flexDirection='column' width='100%' maxWidth='1200px'>
                <Box display='flex' gap={2} sx={{mt: 2}}>
                <Button
                    onClick={handleLoad}
                    variant='contained'
                        disabled={isLoading}
                >
                        {isLoading ? 'Loading...' : 'Load Data'}
                </Button>
                <Button
                    onClick={() => setLoadedData(null)}
                        variant='outlined'
                        disabled={isLoading}
                >
                    Clear Data
                </Button>
                </Box>
                
                {loadedData && (
                    <Box sx={{mt: 3}}>
                        <Typography variant="h6" gutterBottom>
                            Loaded {loadedData.length} items from {integrationType}
                        </Typography>
                        
                        <Box sx={{ maxHeight: 600, overflow: 'auto', border: '1px solid #e0e0e0', borderRadius: 1, p: 2 }}>
                            {loadedData.map((item, index) => (
                                <Card key={item.id || index} sx={{ mb: 2, boxShadow: 1 }}>
                                    <CardContent>
                                        <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                                            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                                                {item.name || 'Unnamed Item'}
                                            </Typography>
                                            <Chip 
                                                label={item.type} 
                                                size="small" 
                                                color={getTypeColor(item.type)}
                                                variant="outlined"
                                            />
                                        </Box>
                                        
                                        <Box sx={{ ml: 1 }}>
                                            <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                                                <strong>ID:</strong> {item.id}
                                            </Typography>
                                            
                                            {item.parent_path_or_name && (
                                                <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                                                    <strong>Parent:</strong> {item.parent_path_or_name}
                                                </Typography>
                                            )}
                                            
                                            <Box display="flex" gap={2} sx={{ mt: 1 }}>
                                                {item.creation_time && (
                                                    <Typography variant="body2" color="text.secondary">
                                                        <strong>Created:</strong> {formatDate(item.creation_time)}
                                                    </Typography>
                                                )}
                                                {item.last_modified_time && (
                                                    <Typography variant="body2" color="text.secondary">
                                                        <strong>Modified:</strong> {formatDate(item.last_modified_time)}
                                                    </Typography>
                                                )}
                                            </Box>
                                            
                                            {item.url && (
                                                <Typography variant="body2" color="primary" sx={{mt: 1}}>
                                                    <a href={item.url} target="_blank" rel="noopener noreferrer">
                                                        Open in {integrationType}
                                                    </a>
                                                </Typography>
                                            )}
                                        </Box>
                                    </CardContent>
                                </Card>
                            ))}
                        </Box>
                    </Box>
                )}
            </Box>
        </Box>
    );
}
