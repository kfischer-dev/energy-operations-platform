import { useEffect, useState } from 'react';
import { getHealth, getDbHealth } from '../api/api';
import './ConnectionStatus.css';

type StatusType = 'loading' | 'success' | 'error';
type ServiceType = 'api' | 'db';

type StatusProps = {
    refreshTrigger: number;
    onCheckComplete: (service: ServiceType) => void;
};

const statusLabels: Record<StatusType, string> = {
    loading: 'Connecting...',
    success: 'Connected',
    error: 'Disconnected',
};

export function ApiStatus({ refreshTrigger, onCheckComplete }: StatusProps) {
    const [status, setStatus] = useState<StatusType>('loading');

    useEffect(() => {
        let active = true;

        async function checkHealth() {
            setStatus('loading');
            try {
                await getHealth();
                if (active) setStatus('success');
            } catch {
                if (active) setStatus('error');
            } finally {
                if (active) onCheckComplete('api');
            }
        }

        void checkHealth();
        return () => {
            active = false;
        };
    }, [refreshTrigger, onCheckComplete]);

    return (
        <div className="api-status" role="status">
            <span className={`status-dot ${status}`} aria-hidden="true" />
            <span>API {statusLabels[status]}</span>
        </div>
    );
}

export function DbStatus({ refreshTrigger, onCheckComplete }: StatusProps) {
    const [status, setStatus] = useState<StatusType>('loading');

    useEffect(() => {
        let active = true;

        async function checkDbHealth() {
            setStatus('loading');
            try {
                await getDbHealth();
                if (active) setStatus('success');
            } catch {
                if (active) setStatus('error');
            } finally {
                if (active) onCheckComplete('db');
            }
        }

        void checkDbHealth();
        return () => {
            active = false;
        };
    }, [refreshTrigger, onCheckComplete]);

    return (
        <div className="db-status" role="status">
            <span className={`db-logo ${status}`} aria-hidden="true" />
            <span>DB {statusLabels[status]}</span>
        </div>
    );
}
