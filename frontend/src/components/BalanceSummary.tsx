import { useEffect, useState } from 'react';
import { getBalanceSummary } from '../api/api';
import type { DashboardCardVisibility } from '../pages/dashboardCards';
import type { BalanceSummary } from '../types/balance';
import { formatEnergy } from '../utils/energy';
import { KpiCard } from './KpiCard';
import './BalanceSummary.css';

type BalanceStatus = 'loading' | 'success' | 'error';

type BalanceSummaryProps = {
    startTime: string | undefined;
    endTime: string | undefined;
    visibleCards: DashboardCardVisibility;
};

function BalanceSummaryComponent({
    startTime = '2026-09-01T00:00:00+02:00',
    endTime = '2026-09-02T00:00:00+02:00',
    visibleCards,
}: BalanceSummaryProps) {

    const [balanceSummary, setBalanceSummary] = useState<BalanceSummary | null>(null);
    const [status, setStatus] = useState<BalanceStatus>('loading');

    useEffect(() => {
        const loadBalanceSummary = async () => {
            setStatus('loading');

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
    }, [startTime, endTime]);

    const production = balanceSummary
        ? formatEnergy(balanceSummary.total_production_energy_kwh)
        : null;

    const consumption = balanceSummary
        ? formatEnergy(balanceSummary.total_consumption_energy_kwh)
        : null;

    const netBalance = balanceSummary
        ? formatEnergy(balanceSummary.total_net_energy_kwh)
        : null;

    return (
        <div className="balance-summary">
            {status === 'success' && balanceSummary ? (
                <div className="kpi-grid">
                    {visibleCards.production && <KpiCard
                        title="Production Energy"
                        value={production?.value ?? 0}
                        unit={production?.unit ?? 'kWh'}
                    />}
                    {visibleCards.consumption && <KpiCard
                        title="Consumption Energy"
                        value={consumption?.value ?? 0}
                        unit={consumption?.unit ?? 'kWh'}
                    />}
                    {visibleCards.net && <KpiCard
                        title="Total Net Energy"
                        value={netBalance?.value ?? 0}
                        unit={netBalance?.unit ?? 'kWh'}
                    />}
                    {visibleCards.peak && <KpiCard
                        title="Peak Power Deficit"
                        value={null}
                        unit=""
                    />}
                </div>
            ) : (
                <div className={`balance-message balance-message--${status}`}>
                    {status === 'loading' && <p>Loading balance summary...</p>}
                    {status === 'error' && <p>Error loading balance summary.</p>}
                </div>
            )}
        </div>
    );
}

export default BalanceSummaryComponent;
