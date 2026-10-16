
import { useEffect, useState } from 'react';
import BalanceSummaryComponent from '../components/BalanceSummary'
import { EnergyMixChart } from '../components/EnergyMixChart';
import { TimeRangeCard } from '../components/TimeRangeCard';
import './Dashboard.css'
import { getBalanceSeries, getEnergyMixProducer, getEnergyMixConsumer } from '../api/api';
import { EnergyBalanceChart } from '../components/BalanceChart';
import type { BalanceInterval, EnergyMix } from '../types/balance';

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
    const [productionMix, setProductionMix] = useState<EnergyMix | null>(null);
    const [consumerMix, setConsumerMix] = useState<EnergyMix | null>(null);

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

        async function fetchEnergyMix() {
            try {
                const producerData = await getEnergyMixProducer(startTime, endTime);
                const consumerData = await getEnergyMixConsumer(startTime, endTime);

                if (active) {
                    setProductionMix(producerData);
                    setConsumerMix(consumerData);
                }

            } catch (error) {
                if (active) {
                    console.error('Energy mix error:', error);
                    setProductionMix(null);
                    setConsumerMix(null);
                }
            }
        }

        fetchEnergyMix();
        fetchBalanceSeries();

        return () => {
            active = false;
        };
    }, [timeRange]);

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
                        startTime={timeRange.startTime}
                        endTime={timeRange.endTime}
                    />
                </div>
                <div className="energy-mix-section">
                    <EnergyMixChart
                        data={productionMix}
                        title="Production Energy Mix"
                    />
                    <EnergyMixChart
                        data={consumerMix}
                        title="Consumer Energy Mix"
                    />
                </div>
            </div>

        </div>
    );
}