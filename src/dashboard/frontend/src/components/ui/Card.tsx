import { ReactNode } from 'react';
import clsx from 'clsx';

interface CardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
}

export function Card({ children, className, hover = false }: CardProps) {
  return (
    <div 
      className={clsx(
        'bg-dark-800/80 border border-dark-700 rounded-xl p-6 backdrop-blur-sm',
        hover && 'hover:border-dark-600 hover:bg-dark-800 transition-all duration-200 cursor-pointer',
        className
      )}
    >
      {children}
    </div>
  );
}

interface CardHeaderProps {
  title: string;
  subtitle?: string;
  action?: ReactNode;
}

export function CardHeader({ title, subtitle, action }: CardHeaderProps) {
  return (
    <div className="flex items-start justify-between mb-4">
      <div>
        <h3 className="text-lg font-semibold text-white">{title}</h3>
        {subtitle && <p className="text-sm text-dark-400 mt-0.5">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

