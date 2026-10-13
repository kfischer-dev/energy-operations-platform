import type { ReactNode } from 'react';
import { Header } from './Header';
import { Sidebar } from './Sidebar'; 
import './MainLayout.css';


type MainLayoutProps = {
  children: ReactNode;
};

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="main-layout">
      <Header />
      <Sidebar />

      <main className="main-content">
        {children}
      </main>
    </div>
  );
}
