import { getHealth } from '../api/api'
import { useState, useEffect } from 'react'
import './ApiStatus.css'

type ApiStatusType = 'loading' | 'success' | 'error';

const statusLabels: Record<ApiStatusType, string> = {
    loading: 'Connecting API...',
    success: 'API Connected',
    error: 'API Disconnected',
};

export function ApiStatus() {

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
            <span className={`status-dot ${status}`} />
            <span>{statusLabels[status]}</span>
        </div>
    );
}