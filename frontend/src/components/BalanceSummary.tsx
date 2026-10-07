import { useEffect, useState } from 'react';
import { getBalanceSummary } from '../api/api';
import type { BalanceSummary } from '../types/balance';

type BalanceStatusType = 'loading' | 'success' | 'error';

function BalanceSummaryComponent() {

    const [balanceSummary, setBalanceSummary] = useState<BalanceSummary | null>(null);
    const [status, setStatus] = useState<BalanceStatusType>('loading');
    
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
                <div>
                    <h1>Balance Summary</h1>
                    <p>Start time: {balanceSummary.start_time}</p>
                    <p>End time: {balanceSummary.end_time}</p>
                    <p>Total Production Energy (kWh): {balanceSummary.total_production_energy_kwh}</p>
                    <p>Total Consumption Energy (kWh): {balanceSummary.total_consumption_energy_kwh}</p>
                    <p>Total Net Energy (kWh): {balanceSummary.total_net_energy_kwh}</p>
                    <p>Quality Status: {balanceSummary.quality_status}</p>
                </div>
            )}
        </div>
    );
}

export default BalanceSummaryComponent;