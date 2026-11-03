import type { TooltipContentProps } from 'recharts';

type EnergyMixTooltipEntry = {
  name: string;
  value: number;
  share: number;
  assetCount: number;
  fill: string;
};

export function EnergyMixTooltip({
  active,
  payload,
}: TooltipContentProps) {
  if (!active || !payload?.length) return null;

  const item = payload[0].payload as EnergyMixTooltipEntry;

  function formatEnergy(value: number): string {
    const abs = Math.abs(value);

    const divisor =
      abs >= 1_000_000 ? 1_000_000 :
      abs >= 1_000 ? 1_000 : 1;

    const unit =
      divisor === 1_000_000 ? 'GWh' :
      divisor === 1_000 ? 'MWh' : 'kWh';

    return `${(value / divisor).toLocaleString('de-DE', {
      maximumFractionDigits: 2,
    })} ${unit}`;
  }

  return (
    <div className="energy-mix-tooltip">
      <div className="energy-mix-tooltip-header">
        <span
          className="energy-mix-tooltip-dot"
          style={{ backgroundColor: item.fill }}
        />
        <strong>{item.name}</strong>
      </div>

      <div className="energy-mix-tooltip-divider" />

      <div className="energy-mix-tooltip-row">
        <span>Energy</span>
        <strong>{formatEnergy(item.value)}</strong>
      </div>

      <div className="energy-mix-tooltip-row">
        <span>Share</span>
        <strong>
          {item.share.toLocaleString('de-DE', {
            maximumFractionDigits: 2,
          })} %
        </strong>
      </div>

      <div className="energy-mix-tooltip-row">
        <span>Assets</span>
        <strong>{item.assetCount}</strong>
      </div>
    </div>
  );
}