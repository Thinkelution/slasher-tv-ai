import { create } from 'zustand';
import type { Dealer, Listing } from '@/types';

interface AppState {
  // Current selections
  selectedDealer: Dealer | null;
  selectedListing: Listing | null;
  
  // UI state
  sidebarOpen: boolean;
  theme: 'dark' | 'light';
  
  // Actions
  setSelectedDealer: (dealer: Dealer | null) => void;
  setSelectedListing: (listing: Listing | null) => void;
  toggleSidebar: () => void;
  toggleTheme: () => void;
}

export const useStore = create<AppState>((set) => ({
  // Initial state
  selectedDealer: null,
  selectedListing: null,
  sidebarOpen: true,
  theme: 'dark',
  
  // Actions
  setSelectedDealer: (dealer) => set({ selectedDealer: dealer }),
  setSelectedListing: (listing) => set({ selectedListing: listing }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  toggleTheme: () => set((state) => ({ 
    theme: state.theme === 'dark' ? 'light' : 'dark' 
  })),
}));

