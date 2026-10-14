import {
    ResponsiveContainer,
    LineChart,
    CartesianGrid,
    XAxis,
    YAxis,
    Tooltip,
    Legend,
    Line,
} from 'recharts';
import './BalanceChart.css';
import type { BalanceInterval } from '../types/balance';


type EnergyBalanceChartProps = {
    data: BalanceInterval[];
};

export function EnergyBalanceChart({ data }: EnergyBalanceChartProps) {
    console.log(data);

    return (
        <div className="energy-balance-chart">
            <ResponsiveContainer width="100%" height={350}>
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" />

                    <XAxis dataKey="interval_start" />
                    <YAxis />

                    <Tooltip />
                    <Legend />

                    <Line
                        type="linear"
                        dataKey="avg_production_power_kw"
                        stroke="#B87333"
                    />

                    <Line
                        type="linear"
                        dataKey="avg_consumption_power_kw"
                        stroke="#38BDF8"
                    />

                    <Line
                        type="linear"
                        dataKey="avg_net_power_kw"
                        stroke="#34D399"
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}