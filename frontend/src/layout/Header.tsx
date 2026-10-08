import { useCallback, useRef, useState } from 'react';
import logo from '../assets/logos/EOP_Logo.png';
import { ApiStatus, DbStatus } from '../components/ConnectionStatus';
import './Header.css';

type ServiceType = 'api' | 'db';

export function Header() {
    const [refreshTrigger, setRefreshTrigger] = useState(0);
    const [isRefreshing, setIsRefreshing] = useState(true);
    const [lastChecked, setLastChecked] = useState<Date | null>(null);
    const completedChecks = useRef<Set<ServiceType>>(new Set());

    // Both checks must finish, even if one reports an error.
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
        <header className="header">
            <div className="logo-area">
                <div className="logo-card">
                    <img src={logo} alt="Energy Operations Platform Logo" />
                </div>
            </div>

            <div className="header-panel">
                <div className="header-left">
                    <h1>Energy Dashboard</h1>
                </div>

                <div className="header-right">
                    <ApiStatus
                        refreshTrigger={refreshTrigger}
                        onCheckComplete={handleCheckComplete}
                    />
                    <DbStatus
                        refreshTrigger={refreshTrigger}
                        onCheckComplete={handleCheckComplete}
                    />

                    <span className="last-checked">
                        {lastChecked
                            ? `Last checked: ${lastChecked.toLocaleTimeString('de-DE')}`
                            : 'Checking...'}
                    </span>

                    <button
                        type="button"
                        className="refresh-button"
                        onClick={handleRefresh}
                        disabled={isRefreshing}
                        aria-label="Check API and database connections again"
                    >
                        {isRefreshing ? 'Refreshing...' : 'Refresh'}
                    </button>
                </div>
            </div>
        </header>
    );
}
