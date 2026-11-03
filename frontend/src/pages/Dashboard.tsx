import { useEffect, useState } from 'react';
import { getBalanceSeries, getEnergyMixProducer, getEnergyMixConsumer } from '../api/api';
import { getAssets } from '../api/api';
import { AssetOverview } from '../components/AssetOverview';
import { EnergyBalanceChart } from '../components/BalanceChart';
import BalanceSummaryComponent from '../components/BalanceSummary'
import { EnergyMixChart } from '../components/EnergyMixChart';
import { TimeRangeCard } from '../components/TimeRangeCard';
import type { AssetResponse } from '../types/assets';
import type { BalanceInterval, EnergyMix } from '../types/balance';
import { allDashboardCardsVisible, dashboardCards } from './dashboardCards';
import type { DashboardCardId } from './dashboardCards';
import './Dashboard.css'
import './DashboardContent.css';
import './DashboardCardSelector.css';

type TimeRange = {
    startTime: string;
    endTime: string;
};

export function Dashboard() {
    const [visibleCards, setVisibleCards] = useState({ ...allDashboardCardsVisible });
    const [timeRange, setTimeRange] = useState<TimeRange>({
        startTime: '2026-09-01T00:00:00+02:00',
        endTime: '2026-09-02T00:00:00+02:00',
    });
    const [series, setSeries] = useState<BalanceInterval[]>([]);
    const [productionMix, setProductionMix] = useState<EnergyMix | null>(null);
    const [consumerMix, setConsumerMix] = useState<EnergyMix | null>(null);
    const [assets, setAssets] = useState<AssetResponse[]>([]);

    function handleApply(startTime: string, endTime: string) {
        setTimeRange({ startTime, endTime });
    }

    function toggleCard(id: DashboardCardId) {
        setVisibleCards(previous => ({ ...previous, [id]: !previous[id] }));
    }

    useEffect(() => {
        const { startTime, endTime } = timeRange;
        let active = true;

        async function fetchAssets() {
            try {
                const data = await getAssets();

                if (active) {
                    setAssets(data);
                }
            } catch (error) {
                if (active) {
                    console.error('Assets error:', error);
                    setAssets([]);
                }
            }
        }

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

        fetchAssets();
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
                    <span className="dashboard-label">DASHBOARD / 01</span>
                    <h1>Energy Overview</h1>
                    <p>System performance and energy balance</p>
                </div>
                <details className="dashboard-card-selector">
                    <summary>Choose cards <span>{Object.values(visibleCards).filter(Boolean).length} / {dashboardCards.length}</span></summary>
                    <fieldset>
                        <legend>Visible cards</legend>
                        {dashboardCards.map(card => (
                            <label key={card.id}>
                                <input type="checkbox" checked={visibleCards[card.id]} onChange={() => toggleCard(card.id)} />
                                <span>{card.label}</span>
                            </label>
                        ))}
                        <p>Time Range is always visible.</p>
                    </fieldset>
                </details>
            </div>

            <div className="dashboard-content">
                <div className="dashboard-overview">
                    <TimeRangeCard
                        onApply={handleApply}
                    />
                    {(visibleCards.production || visibleCards.consumption || visibleCards.net || visibleCards.peak) && <BalanceSummaryComponent
                        startTime={timeRange.startTime}
                        endTime={timeRange.endTime}
                        visibleCards={visibleCards}
                    />}
                </div>
                {visibleCards.balance && <div className="balance-chart">
                    <EnergyBalanceChart
                        data={series}
                        startTime={timeRange.startTime}
                        endTime={timeRange.endTime}
                    />
                </div>}
                {(visibleCards.productionMix || visibleCards.consumerMix || visibleCards.assets) && <div className="energy-mix-section">
                    {visibleCards.productionMix && <EnergyMixChart
                        data={productionMix}
                        title="Production Energy Mix"
                    />}
                    {visibleCards.consumerMix && <EnergyMixChart
                        data={consumerMix}
                        title="Consumer Energy Mix"
                    />}
                    {visibleCards.assets && <div className="asset-overview-section">
                        <AssetOverview assets={assets} />
                    </div>}
                </div>}

            </div>

        </div>
    );
}
