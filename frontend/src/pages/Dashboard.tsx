
import { useState } from 'react';
import BalanceSummaryComponent from '../components/BalanceSummary'
import { TimeRangeCard } from '../components/TimeRangeCard';
import './Dashboard.css'

type TimeRange = {
    startTime: string;
    endTime: string;
};

export function Dashboard() {
    const [timeRange, setTimeRange] = useState<TimeRange | null>(null);

    function handleApply(startTime: string, endTime: string) {
        setTimeRange({ startTime, endTime });
    }

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
                        startTime={timeRange?.startTime}
                        endTime={timeRange?.endTime}
                    />
                </div>
            </div>

        </div>
    );
}