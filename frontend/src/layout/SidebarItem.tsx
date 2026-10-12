import { NavLink } from 'react-router';

type SidebarItemProps = {
  label: string;
  to: string;
  icon?: React.ReactNode;
};

export function SidebarItem({
  label,
  to,
  icon,
}: SidebarItemProps) {
  return (
    <NavLink
      to={to}
      end={to === '/'}
      className={({ isActive }) =>
        `sidebar-item ${isActive ? 'sidebar-item--active' : ''}`
      }
    >
      {icon}
      <span>{label}</span>
    </NavLink>
  );
}