import type { ReactNode } from 'react';
import { ModernHeader } from './ModernHeader';
import { Sidebar } from './Sidebar'; 
import './MainLayout.css';


type MainLayoutProps = {
  children: ReactNode;
};

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="main-layout">
      <ModernHeader />
      <Sidebar />

      <main className="main-content">
        {children}
      </main>
    </div>
  );
}
