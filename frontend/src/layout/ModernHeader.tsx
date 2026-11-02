import { useCallback, useRef, useState } from 'react';
import logo from '../assets/logos/EOP_Logo_2.png';
import { ApiStatus, DbStatus } from '../components/ConnectionStatus';
import './ModernHeader.css';

type ServiceType = 'api' | 'db';

export function ModernHeader() {
    const [refreshTrigger, setRefreshTrigger] = useState(0);
    const [isRefreshing, setIsRefreshing] = useState(true);
    const [lastChecked, setLastChecked] = useState<Date | null>(null);
    const completedChecks = useRef<Set<ServiceType>>(new Set());

    const handleCheckComplete = useCallback((service: ServiceType) => {
        completedChecks.current.add(service);
        if (completedChecks.current.size === 2) {
            setLastChecked(new Date());
            setIsRefreshing(false);
        }
    }, []);

    function handleRefresh() {
        if (isRefreshing) return;
        completedChecks.current.clear();
        setIsRefreshing(true);
        setRefreshTrigger(previous => previous + 1);
    }

    return (
        <header className="modern-header">
            <div className="modern-header__brand">
                <img src={logo} alt="Energy Operations Platform Logo" />
            </div>

            <div className="modern-header__content">
                <h1 className="modern-header__title">Energy Operations <span>Platform</span></h1>

                <div className="modern-header__connections">
                    <div className="modern-header__statuses" role="group" aria-label="Connection status">
                        <ApiStatus refreshTrigger={refreshTrigger} onCheckComplete={handleCheckComplete} />
                        <DbStatus refreshTrigger={refreshTrigger} onCheckComplete={handleCheckComplete} />
                    </div>
                    <button
                        type="button"
                        className="modern-header__refresh"
                        onClick={handleRefresh}
                        disabled={isRefreshing}
                        aria-label="Check API and database connections again"
                    >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                            <path d="M20 7v5h-5M4 17v-5h5" />
                            <path d="M6.1 7a7 7 0 0 1 11.5-1L20 9M4 15l2.4 3A7 7 0 0 0 17.9 17" />
                        </svg>
                        <span>{isRefreshing ? 'Refreshing...' : 'Refresh'}</span>
                    </button>
                    <span className="modern-header__timestamp" aria-live="polite">
                        {lastChecked
                            ? `Last checked: ${lastChecked.toLocaleTimeString('de-DE')}`
                            : 'Checking...'}
                    </span>
                </div>
            </div>
        </header>
    );
}
