type SidebarItemProps = {
  label: string;
  icon?: React.ReactNode;
  active?: boolean;
};

export function SidebarItem({
  label,
  icon,
  active = false,
}: SidebarItemProps) {
  return (
    <button
      className={`sidebar-item ${active ? 'sidebar-item--active' : ''}`}
    >
      {icon}
      <span>{label}</span>
    </button>
  );
}