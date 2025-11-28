import { Bell, Search, User } from 'lucide-react';
import { useStore } from '@/store/useStore';
import clsx from 'clsx';

interface HeaderProps {
  title: string;
  subtitle?: string;
}

export function Header({ title, subtitle }: HeaderProps) {
  const { sidebarOpen, selectedDealer } = useStore();

  return (
    <header 
      className={clsx(
        'fixed top-0 right-0 h-16 bg-dark-900/80 backdrop-blur-xl border-b border-dark-700 z-30',
        'transition-all duration-300',
        sidebarOpen ? 'left-64' : 'left-20'
      )}
    >
      <div className="h-full flex items-center justify-between px-6">
        {/* Title */}
        <div>
          <h1 className="text-xl font-semibold text-white">{title}</h1>
          {subtitle && <p className="text-sm text-dark-400">{subtitle}</p>}
        </div>

        {/* Right side */}
        <div className="flex items-center gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-400" />
            <input 
              type="text"
              placeholder="Search..."
              className="w-64 pl-10 pr-4 py-2 bg-dark-800 border border-dark-600 rounded-lg
                       text-sm text-white placeholder-dark-400 focus:outline-none 
                       focus:border-primary-500 transition-colors"
            />
          </div>

          {/* Current Dealer */}
          {selectedDealer && (
            <div className="px-3 py-1.5 bg-dark-800 border border-dark-600 rounded-lg">
              <span className="text-xs text-dark-400">Dealer:</span>
              <span className="ml-2 text-sm font-medium text-white">{selectedDealer.name}</span>
            </div>
          )}

          {/* Notifications */}
          <button className="relative p-2 rounded-lg hover:bg-dark-700 text-dark-300 hover:text-white transition-colors">
            <Bell className="w-5 h-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-primary-500 rounded-full" />
          </button>

          {/* User */}
          <button className="flex items-center gap-2 p-2 rounded-lg hover:bg-dark-700 transition-colors">
            <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-white" />
            </div>
          </button>
        </div>
      </div>
    </header>
  );
}

