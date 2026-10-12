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
                </div>
            </div>
        </aside>
    );
}