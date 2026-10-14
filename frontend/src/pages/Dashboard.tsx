
import { useEffect, useState } from 'react';
import BalanceSummaryComponent from '../components/BalanceSummary'
import { TimeRangeCard } from '../components/TimeRangeCard';
import './Dashboard.css'
import { getBalanceSeries } from '../api/api';
import { EnergyBalanceChart } from '../components/BalanceChart';
import type { BalanceInterval } from '../types/balance';

type TimeRange = {
    startTime: string;
    endTime: string;
};

export function Dashboard() {
    const [timeRange, setTimeRange] = useState<TimeRange>({
        startTime: '2026-09-01T00:00:00+02:00',
        endTime: '2026-09-02T00:00:00+02:00',
    });
    const [series, setSeries] = useState<BalanceInterval[]>([]);

    function handleApply(startTime: string, endTime: string) {
        setTimeRange({ startTime, endTime });
    }

    useEffect(() => {
        const { startTime, endTime } = timeRange;
        let active = true;

        async function fetchBalanceSeries() {
            try {
                const data = await getBalanceSeries(startTime, endTime, 15);

                if (active) {
                    setSeries(data);
                }
            } catch (error) {
                if (active) {
                    console.error('Balance series error:', error);
                    setSeries([]);
                }
            }
        }

        fetchBalanceSeries();

        return () => {
            active = false;
        };
    }, [timeRange]);

    console.log('Fetched balance series:', series);
    return (
        <div className="dashboard">

            <div className="dashboard-heading">
                <div className="dashboard-title">
                    <h1>Energy Overview</h1>
                    <p>System performance and energy balance</p>
                </div>
            </div>

            <div className="dashboard-content">
                <div className="dashboard-overview">
                    <TimeRangeCard
                        onApply={handleApply}
                    />
                    <BalanceSummaryComponent
                        startTime={timeRange.startTime}
                        endTime={timeRange.endTime}
                    />
                </div>
                <div className="balance-chart">
                    <EnergyBalanceChart
                        data={series}
                    />
                </div>
            </div>

        </div>
    );
}