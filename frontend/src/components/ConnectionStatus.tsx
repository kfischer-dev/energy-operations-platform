import { getHealth, getDbHealth } from '../api/api'
import { useState, useEffect } from 'react'
import './ConnectionStatus.css'

type StatusType = 'loading' | 'success' | 'error';

const statusLabels: Record<StatusType, string> = {
    loading: 'Connecting...',
    success: 'Connected',
    error: 'Disconnected',
};

// API Connection
export function ApiStatus() {

    const [status, setStatus] = useState<StatusType>('loading');

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
            <span>{'API ' + statusLabels[status]}</span>
        </div>
    );
}

// DB Connection
export function DbStatus() {

    const [status, setStatus] = useState<StatusType>('loading');

    useEffect(() => {
        const checkDbHealth = async () => {
            try {
                await getDbHealth();
                setStatus('success');
            } catch {
                setStatus('error');
            }
        };
        checkDbHealth();
    }, []);

    return (
        <div className="db-status">
            <span
                className={`db-logo ${status}`}
                role="img"
                aria-label="Database"
            />
            <span>{
                'DB ' 
                + statusLabels[status]}
            </span>
        </div>
    );
}