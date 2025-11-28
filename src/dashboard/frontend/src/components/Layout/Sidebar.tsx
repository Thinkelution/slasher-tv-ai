import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Users, 
  FileText, 
  Video, 
  QrCode, 
  Settings,
  ChevronLeft,
  Tv,
  Bike
} from 'lucide-react';
import { useStore } from '@/store/useStore';
import clsx from 'clsx';

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/dealers', icon: Users, label: 'Dealers' },
  { path: '/listings', icon: Bike, label: 'Listings' },
  { path: '/scripts', icon: FileText, label: 'Scripts' },
  { path: '/videos', icon: Video, label: 'Videos' },
  { path: '/qr-codes', icon: QrCode, label: 'QR Codes' },
  { path: '/fast-channel', icon: Tv, label: 'FAST Channel' },
  { path: '/settings', icon: Settings, label: 'Settings' },
];

export function Sidebar() {
  const location = useLocation();
  const { sidebarOpen, toggleSidebar } = useStore();

  return (
    <aside 
      className={clsx(
        'fixed left-0 top-0 h-screen bg-dark-900 border-r border-dark-700 z-40',
        'transition-all duration-300 ease-in-out',
        sidebarOpen ? 'w-64' : 'w-20'
      )}
    >
      {/* Logo */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-dark-700">
        <Link to="/" className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
            <Tv className="w-6 h-6 text-white" />
          </div>
          {sidebarOpen && (
            <div className="animate-fade-in">
              <h1 className="font-display text-xl text-white tracking-wide">SLASHER TV</h1>
              <p className="text-xs text-dark-400 -mt-1">AI Dashboard</p>
            </div>
          )}
        </Link>
        <button 
          onClick={toggleSidebar}
          className={clsx(
            'p-2 rounded-lg hover:bg-dark-700 text-dark-400 hover:text-white transition-all',
            !sidebarOpen && 'rotate-180'
          )}
        >
          <ChevronLeft className="w-5 h-5" />
        </button>
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-1">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path || 
            (item.path !== '/' && location.pathname.startsWith(item.path));
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200',
                isActive 
                  ? 'bg-primary-600/20 text-primary-400 border border-primary-500/30' 
                  : 'text-dark-300 hover:bg-dark-700/50 hover:text-white'
              )}
            >
              <item.icon className={clsx('w-5 h-5 flex-shrink-0', isActive && 'text-primary-400')} />
              {sidebarOpen && (
                <span className="font-medium animate-fade-in">{item.label}</span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      {sidebarOpen && (
        <div className="absolute bottom-4 left-4 right-4 animate-fade-in">
          <div className="p-4 rounded-lg bg-gradient-to-br from-primary-600/20 to-primary-800/20 border border-primary-500/20">
            <p className="text-sm text-dark-300">
              <span className="text-primary-400 font-medium">Pro Tip:</span> Use keyboard shortcuts for faster navigation
            </p>
          </div>
        </div>
      )}
    </aside>
  );
}

