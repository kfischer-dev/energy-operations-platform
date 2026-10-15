import type { TooltipContentProps } from 'recharts';
import type { BalanceInterval } from '../types/balance';
import './BalanceChartTooltip.css';

type ChartInterval = BalanceInterval & {
    timestamp: number;
};

type BalanceChartTooltipProps =
    TooltipContentProps & {
        powerDivisor: number;
        powerUnit: string;
    };

export function BalanceChartTooltip({
    active,
    payload,
    powerDivisor,
    powerUnit,
}: BalanceChartTooltipProps) {
    if (!active || !payload?.length) return null;

    const interval = payload[0].payload as ChartInterval;

    const formatPower = (value: number) =>
        `${new Intl.NumberFormat('de-DE', {
            maximumFractionDigits: 2,
        }).format(value / powerDivisor)} ${powerUnit}`;

    const formatDate = (value: string) =>
        new Date(value).toLocaleDateString('de-DE', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
        });

    const formatClock = (value: string) =>
        new Date(value).toLocaleTimeString('de-DE', {
            hour: '2-digit',
            minute: '2-digit',
        });

    return (
        <div className="balance-chart-tooltip">
            <div className="tooltip-header">
                <strong>{formatDate(interval.interval_start)}</strong>

                <span>
                    {formatClock(interval.interval_start)} –{' '}
                    {formatClock(interval.interval_end)}
                </span>
            </div>

            <p className="tooltip-subtitle">
                Average power per interval
            </p>

            <div className="tooltip-divider" />

            <div className="tooltip-values">
                <div className="tooltip-row">
                    <span className="tooltip-label">
                        <span className="tooltip-dot production" />
                        Production
                    </span>
                    <strong>{formatPower(interval.avg_production_power_kw)}</strong>
                </div>

                <div className="tooltip-row">
                    <span className="tooltip-label">
                        <span className="tooltip-dot consumption" />
                        Consumption
                    </span>
                    <strong>{formatPower(interval.avg_consumption_power_kw)}</strong>
                </div>

                <div className="tooltip-row">
                    <span className="tooltip-label">
                        <span className="tooltip-dot net" />
                        Net Power
                    </span>
                    <strong>{formatPower(interval.avg_net_power_kw)}</strong>
                </div>
            </div>

            <div className="tooltip-divider" />

            <div className="tooltip-quality">
                <span>Data quality</span>
                <span>{interval.quality_status}</span>
            </div>
        </div>
    );
}