import './BalanceSummary.css';

type KpiCardProps = {
  title: string;
  value: number;
  unit: string;
};

export function KpiCard({ title, value, unit }: KpiCardProps) {
  return (
    <div className="kpi-card">
      <h3>{title}</h3>
      <p>
        {value} {unit}
      </p>
    </div>
  );
}
