import { useEffect, useState } from 'react';
import { getBalanceSummary } from '../api/api';
import { formatDateTime } from '../utils/date';
import { KpiCard } from './KpiCard';
import './BalanceSummary.css';
import type { BalanceSummary } from '../types/balance';

type BalanceStatus = 'loading' | 'success' | 'error';

function BalanceSummaryComponent() {

    const [balanceSummary, setBalanceSummary] = useState<BalanceSummary | null>(null);
    const [status, setStatus] = useState<BalanceStatus>('loading');

    const startTime = '2026-09-01T00:00:00+02:00';
    const endTime = '2026-09-02T00:00:00+02:00';

    useEffect(() => {
        const loadBalanceSummary = async () => {
            try {
                const data = await getBalanceSummary(startTime, endTime);
                setBalanceSummary(data);
                setStatus('success');
            } catch {
                setBalanceSummary(null);
                setStatus('error');
            }

        }
        loadBalanceSummary();
    }, []);

    return (
        <div className="balance-summary">
            {status === 'loading' && <p>Loading balance summary...</p>}
            {status === 'error' && <p>Error loading balance summary.</p>}
            {status === 'success' && balanceSummary && (
                <div className="balance-summary-inner">
                    <h1>Balance Summary</h1>
                    <p>Startzeit: {formatDateTime(balanceSummary.start_time)}</p>
                    <p>Endzeit: {formatDateTime(balanceSummary.end_time)}</p>
                    <p>Quality Status: {balanceSummary.quality_status}</p>
                    <div className="kpi-grid">
                        <KpiCard title="Total Production Energy" value={balanceSummary.total_production_energy_kwh} unit="kWh" />
                        <KpiCard title="Total Consumption Energy" value={balanceSummary.total_consumption_energy_kwh} unit="kWh" />
                        <KpiCard title="Total Net Energy" value={balanceSummary.total_net_energy_kwh} unit="kWh" />
                    </div>

                </div>
            )}
        </div>
    );
}

export default BalanceSummaryComponent;