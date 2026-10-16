import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Tooltip,
  Legend,
} from 'recharts';

import './EnergyMixChart.css';
import type { EnergyMix } from '../types/balance';

type EnergyMixChartProps = {
  data: EnergyMix | null;
  title: string;
};

const ASSET_COLORS: Record<string, string> = {
  solar_park: '#F4C95D',
  wind_park: '#38BDF8',
  hydro_power_plant: '#2DD4BF',
  biomass_power_plant: '#84CC16',
  gas_power_plant: '#C88953',

  city_load: '#A78BFA',
  industrial_load: '#F97316',
  residential_load: '#F472B6',
  data_center: '#818CF8',
};

export function EnergyMixChart(
  { data, title }: EnergyMixChartProps
) {

  const chartData = data?.contributions.map((item) => ({
    name: item.asset_type,
    value: item.energy_kwh,
    fill: ASSET_COLORS[item.asset_type] ?? '#94A3B8',
  })) ?? [];

  return (
    <div className="energy-mix-chart">
      <h2>{title}</h2>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            innerRadius={65}
            outerRadius={100}
          />

          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}