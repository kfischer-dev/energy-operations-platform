import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';

type SidebarState = {
  collapsed: boolean;
  toggle: () => void;
};

const SidebarContext = createContext<SidebarState | null>(null);

export function SidebarProvider({ children }: { children: ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <SidebarContext.Provider value={{ collapsed, toggle: () => setCollapsed(previous => !previous) }}>
      {children}
    </SidebarContext.Provider>
  );
}

export function useSidebar() {
  const state = useContext(SidebarContext);
  if (!state) throw new Error('useSidebar must be used within SidebarProvider');
  return state;
}
