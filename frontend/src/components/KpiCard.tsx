import './BalanceSummary.css';
import './KpiCard.css';
import productionIcon from '../assets/icons/balance/bolt.svg';
import balanceIcon from '../assets/icons/balance/balance.svg';
import consumptionIcon from '../assets/icons/balance/city.svg';
import powerDeficitIcon from '../assets/icons/balance/wave-square.svg';
import infoIcon from '../assets/icons/info.svg';

type KpiCardProps = {
  title: string;
  value: number;
  unit: string;
};

export function KpiCard({ title, value, unit }: KpiCardProps) {

  let icon;
  let footer = '';
  switch (title.toLowerCase()) {
    case 'production energy':
      icon = productionIcon;
      footer = 'Total energy generated';
      break;
    case 'consumption energy':
      icon = consumptionIcon;
      footer = 'Total energy consumed';
      break;
    case 'total net energy':
      icon = balanceIcon;
      footer = 'Net energy deficit';
      break;
    case 'peak power deficit':
      icon = powerDeficitIcon;
      footer = 'Available in v0.16';
      break;
    default:
      icon = '';
  }

  return (
    <div className="kpi-card">
      <div className="kpi-card-header">
        <h3>{title}</h3>
        <img src={icon} alt="Icon" />
      </div>
      <div className="kpi-card-value">
        <span>{value}</span>
        <span className="kpi-card-unit">{unit}</span>
      </div>

      <div className="kpi-card-divider"></div>

      <div className="kpi-card-footer">
        <img src={infoIcon} alt="Icon" />
        {footer}
      </div>
    </div>
  );
}
