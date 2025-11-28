import { useQuery } from '@tanstack/react-query';
import { 
  Users, 
  Video, 
  FileText, 
  CheckCircle, 
  Clock, 
  AlertCircle,
  TrendingUp,
  Play
} from 'lucide-react';
import { Layout } from '@/components/Layout';
import { Card, CardHeader } from '@/components/ui';
import { dealerApi, scriptApi, videoApi } from '@/services/api';
import clsx from 'clsx';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: { value: number; positive: boolean };
  color: string;
}

function StatCard({ title, value, icon, trend, color }: StatCardProps) {
  return (
    <Card className="relative overflow-hidden">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-dark-400">{title}</p>
          <p className="text-3xl font-bold text-white mt-1">{value}</p>
          {trend && (
            <div className={clsx(
              'flex items-center gap-1 mt-2 text-sm',
              trend.positive ? 'text-emerald-400' : 'text-red-400'
            )}>
              <TrendingUp className={clsx('w-4 h-4', !trend.positive && 'rotate-180')} />
              <span>{trend.value}% from last week</span>
            </div>
          )}
        </div>
        <div className={clsx(
          'p-3 rounded-xl',
          color
        )}>
          {icon}
        </div>
      </div>
      {/* Decorative gradient */}
      <div className={clsx(
        'absolute -right-8 -bottom-8 w-32 h-32 rounded-full opacity-10 blur-2xl',
        color.replace('bg-', 'bg-').replace('/20', '')
      )} />
    </Card>
  );
}

export function Dashboard() {
  const { data: dealers } = useQuery({
    queryKey: ['dealers'],
    queryFn: dealerApi.getAll,
  });

  const { data: pendingScripts } = useQuery({
    queryKey: ['scripts', 'pending'],
    queryFn: () => scriptApi.getPending(),
  });

  const { data: pendingVideos } = useQuery({
    queryKey: ['videos', 'pending'],
    queryFn: () => videoApi.getPending(),
  });

  const dealerCount = dealers?.data?.length || 0;
  const pendingScriptCount = pendingScripts?.data?.length || 0;
  const pendingVideoCount = pendingVideos?.data?.length || 0;

  return (
    <Layout title="Dashboard" subtitle="Overview of your video production pipeline">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Active Dealers"
          value={dealerCount}
          icon={<Users className="w-6 h-6 text-blue-400" />}
          color="bg-blue-500/20"
          trend={{ value: 12, positive: true }}
        />
        <StatCard
          title="Scripts Pending"
          value={pendingScriptCount}
          icon={<FileText className="w-6 h-6 text-amber-400" />}
          color="bg-amber-500/20"
        />
        <StatCard
          title="Videos to Review"
          value={pendingVideoCount}
          icon={<Video className="w-6 h-6 text-purple-400" />}
          color="bg-purple-500/20"
        />
        <StatCard
          title="Published Today"
          value={0}
          icon={<CheckCircle className="w-6 h-6 text-emerald-400" />}
          color="bg-emerald-500/20"
          trend={{ value: 8, positive: true }}
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <Card className="lg:col-span-2">
          <CardHeader 
            title="Recent Activity" 
            subtitle="Latest updates across all dealers"
          />
          <div className="space-y-4">
            {[
              { icon: Video, text: 'New video generated for 2024 Harley-Davidson', time: '2 min ago', color: 'text-purple-400' },
              { icon: FileText, text: 'Script approved for 2023 Indian Scout', time: '15 min ago', color: 'text-emerald-400' },
              { icon: AlertCircle, text: 'Image processing failed for listing #12345', time: '1 hour ago', color: 'text-red-400' },
              { icon: CheckCircle, text: 'Video published to FAST channel', time: '2 hours ago', color: 'text-emerald-400' },
              { icon: Clock, text: '5 videos queued for processing', time: '3 hours ago', color: 'text-amber-400' },
            ].map((activity, i) => (
              <div key={i} className="flex items-center gap-4 p-3 rounded-lg hover:bg-dark-700/50 transition-colors">
                <div className={clsx('p-2 rounded-lg bg-dark-700', activity.color)}>
                  <activity.icon className="w-4 h-4" />
                </div>
                <div className="flex-1">
                  <p className="text-sm text-white">{activity.text}</p>
                  <p className="text-xs text-dark-400">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader title="Quick Actions" />
          <div className="space-y-3">
            <button className="w-full flex items-center gap-3 p-3 rounded-lg bg-primary-600/20 hover:bg-primary-600/30 border border-primary-500/30 text-primary-400 transition-colors">
              <Play className="w-5 h-5" />
              <span className="font-medium">Run Pipeline</span>
            </button>
            <button className="w-full flex items-center gap-3 p-3 rounded-lg bg-dark-700 hover:bg-dark-600 text-white transition-colors">
              <FileText className="w-5 h-5" />
              <span className="font-medium">Review Scripts</span>
            </button>
            <button className="w-full flex items-center gap-3 p-3 rounded-lg bg-dark-700 hover:bg-dark-600 text-white transition-colors">
              <Video className="w-5 h-5" />
              <span className="font-medium">Approve Videos</span>
            </button>
            <button className="w-full flex items-center gap-3 p-3 rounded-lg bg-dark-700 hover:bg-dark-600 text-white transition-colors">
              <Users className="w-5 h-5" />
              <span className="font-medium">Add Dealer</span>
            </button>
          </div>
        </Card>
      </div>

      {/* Pipeline Status */}
      <Card className="mt-6">
        <CardHeader 
          title="Pipeline Status" 
          subtitle="Current processing queue"
        />
        <div className="flex items-center gap-4">
          {[
            { label: 'Downloading', count: 3, color: 'bg-blue-500' },
            { label: 'Processing Images', count: 2, color: 'bg-purple-500' },
            { label: 'Generating Scripts', count: 5, color: 'bg-amber-500' },
            { label: 'Creating Videos', count: 1, color: 'bg-emerald-500' },
          ].map((stage) => (
            <div key={stage.label} className="flex-1 text-center">
              <div className={clsx(
                'h-2 rounded-full mb-2',
                stage.color,
                stage.count > 0 ? 'animate-pulse' : 'opacity-30'
              )} />
              <p className="text-2xl font-bold text-white">{stage.count}</p>
              <p className="text-xs text-dark-400">{stage.label}</p>
            </div>
          ))}
        </div>
      </Card>
    </Layout>
  );
}

