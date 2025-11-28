import clsx from 'clsx';
import type { ListingStatus } from '@/types';

type BadgeVariant = 'success' | 'warning' | 'error' | 'info' | 'neutral';

interface BadgeProps {
  variant?: BadgeVariant;
  children: React.ReactNode;
  className?: string;
}

const variantStyles: Record<BadgeVariant, string> = {
  success: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  warning: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  error: 'bg-red-500/20 text-red-400 border-red-500/30',
  info: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  neutral: 'bg-dark-600/50 text-dark-300 border-dark-500/30',
};

export function Badge({ variant = 'neutral', children, className }: BadgeProps) {
  return (
    <span 
      className={clsx(
        'inline-flex items-center px-2 py-1 text-xs font-medium rounded-full border',
        variantStyles[variant],
        className
      )}
    >
      {children}
    </span>
  );
}

// Status badge helper
const statusVariants: Record<ListingStatus, BadgeVariant> = {
  pending: 'neutral',
  images_downloaded: 'info',
  images_processed: 'info',
  script_generated: 'warning',
  script_approved: 'success',
  voiceover_generated: 'info',
  video_generated: 'warning',
  video_approved: 'success',
  published: 'success',
  error: 'error',
};

const statusLabels: Record<ListingStatus, string> = {
  pending: 'Pending',
  images_downloaded: 'Images Downloaded',
  images_processed: 'Images Processed',
  script_generated: 'Script Ready',
  script_approved: 'Script Approved',
  voiceover_generated: 'Voiceover Ready',
  video_generated: 'Video Ready',
  video_approved: 'Video Approved',
  published: 'Published',
  error: 'Error',
};

export function StatusBadge({ status }: { status: ListingStatus }) {
  return (
    <Badge variant={statusVariants[status]}>
      {statusLabels[status]}
    </Badge>
  );
}

