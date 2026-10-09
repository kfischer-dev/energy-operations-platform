import './BalanceSummary.css';
import './KpiCard.css';
import productionIcon from '../assets/icons/balance/bolt.svg';
import balanceIcon from '../assets/icons/balance/balance.svg';
import consumptionIcon from '../assets/icons/balance/city.svg';
import powerDeficitIcon from '../assets/icons/balance/wave-square.svg';

type KpiCardProps = {
  title: string;
  value: number;
  unit: string;
};

export function KpiCard({ title, value, unit }: KpiCardProps) {

  let icon;
  switch (title.toLowerCase()) {
    case 'production energy':
      icon = productionIcon;
      break;
    case 'consumption energy':
      icon = consumptionIcon;
      break;
    case 'total net energy':
      icon = balanceIcon;
      break;
    case 'peak power deficit':
      icon = powerDeficitIcon;
      break;
    default:
      icon = '';
  }

  return (
    <div className="kpi-card">
      <div className="header">
        <h3>{title}</h3>
        <img src={icon} alt="Icon" />
      </div>
      <p>
        {value} {unit}
      </p>
    </div>
  );
}
