import { ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { useStore } from '@/store/useStore';
import clsx from 'clsx';

interface LayoutProps {
  children: ReactNode;
  title: string;
  subtitle?: string;
}

export function Layout({ children, title, subtitle }: LayoutProps) {
  const { sidebarOpen } = useStore();

  return (
    <div className="min-h-screen bg-dark-950">
      <Sidebar />
      <Header title={title} subtitle={subtitle} />
      
      <main 
        className={clsx(
          'pt-16 min-h-screen transition-all duration-300',
          sidebarOpen ? 'ml-64' : 'ml-20'
        )}
      >
        <div className="p-6">
          {children}
        </div>
      </main>

      {/* Background decoration */}
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-primary-600/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-primary-800/5 rounded-full blur-3xl" />
      </div>
    </div>
  );
}

