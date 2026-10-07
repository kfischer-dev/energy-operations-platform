import { getHealth } from '../api/api'
import { useState, useEffect } from 'react'

function ApiStatus() {

    type ApiStatusType = 'loading' | 'success' | 'error';

    const [status, setStatus] = useState<ApiStatusType>('loading');

    useEffect(() => {
        const checkHealth = async () => {
            try {
                await getHealth();
                setStatus('success');
            } catch {
                setStatus('error');
            }
        };
        checkHealth();
    }, []);

    return (
        <div className="api-status">
            <p>
                {status === 'loading' && 'Checking API status...'}
                {status === 'success' && 'API is healthy'}
                {status === 'error' && 'Failed to fetch API status'}
            </p>
        </div>
    );
}

export default ApiStatus;