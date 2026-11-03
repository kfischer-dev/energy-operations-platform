import { createContext, useContext } from 'react';

type SidebarState = {
  collapsed: boolean;
  toggle: () => void;
};

export const SidebarContext = createContext<SidebarState | null>(null);

export function useSidebar() {
  const state = useContext(SidebarContext);
  if (!state) throw new Error('useSidebar must be used within SidebarProvider');
  return state;
}
