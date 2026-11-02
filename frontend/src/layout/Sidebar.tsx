import { SidebarItem } from './SidebarItem';
import dashboardIcon from '../assets/icons/dashboard.svg';
import assetsIcon from '../assets/icons/assets.svg';
import balanceIcon from '../assets/icons/balance/balance.svg';
import simulationIcon from '../assets/icons/simulation.svg';
import './Sidebar.css';

export function Sidebar() {
    return (
        <aside className="sidebar">
            <div className="sidebar-panel">
                <div className="sidebar-content">
                    <SidebarItem
                        label="Dashboard"
                        icon={<img src={dashboardIcon} alt="" />}
                        to="/"
                    />

                    <SidebarItem
                        label="Assets"
                        icon={<img src={assetsIcon} alt="" />}
                        to="/assets"
                    />

                    <SidebarItem
                        label="Balance"
                        icon={<img src={balanceIcon} alt="" />}
                        to="/balance"
                    />

                    <SidebarItem
                        label="Simulation"
                        icon={<img src={simulationIcon} alt="" />}
                        to="/simulation"
                    />
                    <SidebarItem
                        label="Design Test"
                        icon={
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
                                <rect x="3" y="4" width="18" height="16" rx="3" />
                                <path d="M3 10h18M9 10v10" />
                            </svg>
                        }
                        to="/design-test"
                    />
                </div>
            </div>
        </aside>
    );
}
