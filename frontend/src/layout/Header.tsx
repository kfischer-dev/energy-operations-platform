import logo from '../assets/logos/EOP_Logo.png';
import { ApiStatus, DbStatus } from '../components/ConnectionStatus';
import './Header.css';

export function Header() {
  return (
    <header className="header">
      <div className="logo-area">
        <div className="logo-card">
          <img src={logo} alt="Logo" />
        </div>
      </div>

      <div className="header-panel">
        <div className="header-left">
          <h1>Energy Dashboard</h1>
        </div>

        <div className="header-right">
          <ApiStatus />
          <DbStatus />
        </div>
      </div>
    </header>
  );
}