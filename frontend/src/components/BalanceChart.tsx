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
import type { BalanceInterval } from '../types/balance';
import { BalanceChartTooltip } from './BalanceChartTooltip';
import './BalanceChart.css';

type EnergyBalanceChartProps = {
    data: BalanceInterval[];
    startTime: string;
    endTime: string;
};

export function EnergyBalanceChart({
    data,
    startTime,
    endTime,
}: EnergyBalanceChartProps) {
    const chartData = data.map((interval) => ({
        ...interval,
        timestamp:
            (new Date(interval.interval_start).getTime() +
                new Date(interval.interval_end).getTime()) / 2,
    }));

    const tickCount = 7;
    const start = new Date(startTime).getTime();
    const end = new Date(endTime).getTime();
    const tickStep = (end - start) / (tickCount - 1);

    const ticks = Array.from(
        { length: tickCount },
        (_, index) => start + index * tickStep
    );

    const maxPower = Math.max(
        0,
        ...data.flatMap((interval) => [
            Math.abs(interval.avg_production_power_kw),
            Math.abs(interval.avg_consumption_power_kw),
            Math.abs(interval.avg_net_power_kw),
        ])
    );

    const powerUnit =
        maxPower >= 1_000_000 ? 'GW' :
            maxPower >= 1_000 ? 'MW' :
                'kW';

    const powerDivisor =
        powerUnit === 'GW' ? 1_000_000 :
            powerUnit === 'MW' ? 1_000 :
                1;

    return (
        <div className="energy-balance-chart">
            <div className="chart-header">
                <div>
                    <h2>Energy Balance</h2>
                    <p>Average power over selected time range</p>
                </div>
            </div>

            <ResponsiveContainer width="100%" height={350}>
                <LineChart data={chartData}>
                    <CartesianGrid
                        stroke="rgba(215, 224, 233, 0.075)"
                        strokeDasharray="3 5"
                        vertical={false}
                    />

                    <XAxis
                        dataKey="timestamp"
                        type="number"
                        scale="time"
                        domain={[
                            new Date(startTime).getTime(),
                            new Date(endTime).getTime(),
                        ]}
                        allowDataOverflow
                        ticks={ticks}
                        minTickGap={20}
                        tickFormatter={(value: number) =>
                            new Date(value).toLocaleTimeString('de-DE', {
                                hour: '2-digit',
                                minute: '2-digit',
                            })
                        }
                        tick={{ fill: '#A5AEBB', fontSize: 12 }}
                        axisLine={{ stroke: 'rgba(215, 224, 233, 0.13)' }}
                        tickLine={false}
                        tickMargin={12}
                        label={{
                            value: 'Time',
                            position: 'insideBottom',
                            offset: -8,
                            fill: '#B8C2CE',
                            fontSize: 14,
                        }}
                        height={40}
                    />

                    <YAxis
                        tick={{ fill: '#A5AEBB', fontSize: 12 }}
                        axisLine={{ stroke: 'rgba(215, 224, 233, 0.13)' }}
                        tickLine={false}
                        width={45}
                        tickFormatter={(value: number) =>
                            new Intl.NumberFormat('de-DE', {
                                maximumFractionDigits: 2,
                            }).format(value / powerDivisor)
                        }
                        label={{
                            value: `Power [${powerUnit}]`,
                            angle: -90,
                            position: 'insideLeft',
                            offset: 0,
                            fill: '#B8C2CE',
                            fontSize: 14,
                        }}
                    />
                    <Tooltip
                        content={(props) => (
                            <BalanceChartTooltip
                                {...props}
                                powerDivisor={powerDivisor}
                                powerUnit={powerUnit}
                            />
                        )}
                        formatter={(value) => {
                            if (typeof value !== 'number') return String(value ?? '');

                            return `${new Intl.NumberFormat('de-DE', {
                                maximumFractionDigits: 2,
                            }).format(value / powerDivisor)} ${powerUnit}`;
                        }}
                    />
                    <Legend
                        iconType="plainline"
                        wrapperStyle={{
                            paddingTop: 16,
                            fontSize: 12,
                            color: '#B8C2CE',
                        }}
                    />

                    <Line
                        type="linear"
                        dataKey="avg_production_power_kw"
                        name="Production"
                        stroke="#C99A6B"
                        strokeWidth={2.2}
                        dot={false}
                        activeDot={{ r: 5 }}
                    />

                    <Line
                        type="linear"
                        dataKey="avg_consumption_power_kw"
                        name="Consumption"
                        stroke="#86B8D1"
                        strokeWidth={2.2}
                        dot={false}
                        activeDot={{ r: 5 }}
                    />

                    <Line
                        type="linear"
                        dataKey="avg_net_power_kw"
                        name="Net Power"
                        stroke="#91B5A3"
                        strokeWidth={1.9}
                        strokeDasharray="4 5"
                        dot={false}
                        activeDot={{ r: 5 }}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}