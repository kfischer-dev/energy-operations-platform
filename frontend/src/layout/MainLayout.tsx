import type { ReactNode } from 'react';
import './MainLayout.css';

type MainLayoutProps = {
  children: ReactNode;
};

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="main-layout">
      <header className="app-header">
        <div className="logo">
          <img src="01_eop_horizontal.png" alt="Logo" />
        </div>
        <div className="header-panel">
          Header
        </div>
      </header>

      <aside className="sidebar">
        <div className="sidebar-panel">
          Sidebar
        </div>
      </aside>

      <main className="main-content">
        {children}
      </main>
    </div>
  );
}
    