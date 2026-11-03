import type { ReactNode } from 'react';
import { ModernHeader } from './ModernHeader';
import { Sidebar } from './Sidebar';
import { useSidebar } from './sidebarContext';
import './MainLayout.css';


type MainLayoutProps = {
  children: ReactNode;
};

export function MainLayout({ children }: MainLayoutProps) {
  const { collapsed } = useSidebar();
  return (
    <div className={`main-layout${collapsed ? ' main-layout--sidebar-collapsed' : ''}`}>
      <ModernHeader />
      <Sidebar />

      <main className="main-content">
        {children}
      </main>
    </div>
  );
}
