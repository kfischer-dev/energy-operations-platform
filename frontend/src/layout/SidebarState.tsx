import { useState } from 'react';
import type { ReactNode } from 'react';
import { SidebarContext } from './sidebarContext';

export function SidebarProvider({ children }: { children: ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <SidebarContext.Provider value={{ collapsed, toggle: () => setCollapsed(previous => !previous) }}>
      {children}
    </SidebarContext.Provider>
  );
}

