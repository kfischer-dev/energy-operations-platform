import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Tooltip,
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

const ASSET_LABELS: Record<string, string> = {
  solar_park: 'Solar Park',
  wind_park: 'Wind Park',
  hydro_power_plant: 'Hydro Power Plant',
  biomass_power_plant: 'Biomass Power Plant',
  gas_power_plant: 'Gas Power Plant',

  city_load: 'City Load',
  industrial_load: 'Industrial Load',
  residential_load: 'Residential Load',
  data_center: 'Data Center',
};

function formatEnergy(valueKwh: number): string {
  if (Math.abs(valueKwh) >= 1_000_000) {
    return `${(valueKwh / 1_000_000).toLocaleString('de-DE', {
      maximumFractionDigits: 2,
    })} GWh`;
  }

  if (Math.abs(valueKwh) >= 1_000) {
    return `${(valueKwh / 1_000).toLocaleString('de-DE', {
      maximumFractionDigits: 2,
    })} MWh`;
  }

  return `${valueKwh.toLocaleString('de-DE', {
    maximumFractionDigits: 2,
  })} kWh`;
}

export function EnergyMixChart(
  { data, title }: EnergyMixChartProps
) {

  const chartData = data?.contributions.map((item) => ({
    name: ASSET_LABELS[item.asset_type] ?? item.asset_type,
    value: item.energy_kwh,
    share: item.share_percent,
    fill: ASSET_COLORS[item.asset_type] ?? '#94A3B8',
  })) ?? [];

  return (
    <section className="energy-mix-chart">
      <div className="energy-mix-header">
        <h2>{title}</h2>
        <p>Energy distribution by asset type</p>
      </div>

      <div className="energy-mix-donut">
        <ResponsiveContainer width="100%" height={260}>
          <PieChart>
            <Pie
              data={chartData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              innerRadius={72}
              outerRadius={105}
              stroke="rgba(255, 255, 255, 0.15)"
              strokeWidth={1}
            />
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>

        <div className="energy-mix-center">
          <span>Total energy</span>
          <strong>
            {data ? formatEnergy(data.total_energy_kwh) : '—'}
          </strong>
        </div>
      </div>

      <div className="energy-mix-legend">
        {chartData.map((item) => (
          <div className="energy-mix-legend-item" key={item.name}>
            <div className="energy-mix-legend-name">
              <span
                className="energy-mix-legend-dot"
                style={{ backgroundColor: item.fill }}
              />
              <span>{item.name}</span>
            </div>
            <strong>
              {item.share.toLocaleString('de-DE', {
                maximumFractionDigits: 2,
              })} %
            </strong>
          </div>
        ))}
      </div>
    </section>
  );
}