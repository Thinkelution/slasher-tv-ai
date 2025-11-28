import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Settings, Trash2, ExternalLink, Upload } from 'lucide-react';
import { Layout } from '@/components/Layout';
import { Card, CardHeader, Button, Badge, Modal } from '@/components/ui';
import { dealerApi } from '@/services/api';
import { useStore } from '@/store/useStore';
import type { Dealer, DealerSettings } from '@/types';
import toast from 'react-hot-toast';

export function Dealers() {
  const queryClient = useQueryClient();
  const { setSelectedDealer } = useStore();
  const [showAddModal, setShowAddModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [selectedDealerForSettings, setSelectedDealerForSettings] = useState<Dealer | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ['dealers'],
    queryFn: dealerApi.getAll,
  });

  const deleteMutation = useMutation({
    mutationFn: dealerApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dealers'] });
      toast.success('Dealer deleted');
    },
    onError: () => toast.error('Failed to delete dealer'),
  });

  const dealers = data?.data || [];

  const handleOpenSettings = (dealer: Dealer) => {
    setSelectedDealerForSettings(dealer);
    setShowSettingsModal(true);
  };

  return (
    <Layout title="Dealers" subtitle="Manage dealer accounts and their settings">
      {/* Actions */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Button onClick={() => setShowAddModal(true)} icon={<Plus className="w-4 h-4" />}>
            Add Dealer
          </Button>
          <Button variant="secondary" icon={<Upload className="w-4 h-4" />}>
            Import CSV
          </Button>
        </div>
      </div>

      {/* Dealers Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <div className="h-6 bg-dark-700 rounded w-3/4 mb-4" />
              <div className="h-4 bg-dark-700 rounded w-1/2 mb-2" />
              <div className="h-4 bg-dark-700 rounded w-2/3" />
            </Card>
          ))}
        </div>
      ) : dealers.length === 0 ? (
        <Card className="text-center py-12">
          <p className="text-dark-400 mb-4">No dealers found</p>
          <Button onClick={() => setShowAddModal(true)} icon={<Plus className="w-4 h-4" />}>
            Add Your First Dealer
          </Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {dealers.map((dealer) => (
            <DealerCard
              key={dealer._id}
              dealer={dealer}
              onSelect={() => setSelectedDealer(dealer)}
              onSettings={() => handleOpenSettings(dealer)}
              onDelete={() => {
                if (confirm('Delete this dealer and all their data?')) {
                  deleteMutation.mutate(dealer.dealerId);
                }
              }}
            />
          ))}
        </div>
      )}

      {/* Add Dealer Modal */}
      <AddDealerModal 
        isOpen={showAddModal} 
        onClose={() => setShowAddModal(false)} 
      />

      {/* Settings Modal */}
      {selectedDealerForSettings && (
        <DealerSettingsModal
          isOpen={showSettingsModal}
          onClose={() => {
            setShowSettingsModal(false);
            setSelectedDealerForSettings(null);
          }}
          dealer={selectedDealerForSettings}
        />
      )}
    </Layout>
  );
}

// Dealer Card Component
function DealerCard({ 
  dealer, 
  onSelect, 
  onSettings, 
  onDelete 
}: { 
  dealer: Dealer;
  onSelect: () => void;
  onSettings: () => void;
  onDelete: () => void;
}) {
  const { data: stats } = useQuery({
    queryKey: ['dealer-stats', dealer.dealerId],
    queryFn: () => dealerApi.getStats(dealer.dealerId),
  });

  return (
    <Card hover className="group">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center text-white font-bold text-lg">
            {dealer.name.charAt(0)}
          </div>
          <div>
            <h3 className="font-semibold text-white">{dealer.name}</h3>
            <p className="text-sm text-dark-400">ID: {dealer.dealerId}</p>
          </div>
        </div>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button 
            onClick={onSettings}
            className="p-2 rounded-lg hover:bg-dark-700 text-dark-400 hover:text-white transition-colors"
          >
            <Settings className="w-4 h-4" />
          </button>
          <button 
            onClick={onDelete}
            className="p-2 rounded-lg hover:bg-red-500/20 text-dark-400 hover:text-red-400 transition-colors"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="p-3 bg-dark-700/50 rounded-lg">
          <p className="text-2xl font-bold text-white">{stats?.data?.totalListings || 0}</p>
          <p className="text-xs text-dark-400">Total Listings</p>
        </div>
        <div className="p-3 bg-dark-700/50 rounded-lg">
          <p className="text-2xl font-bold text-emerald-400">{stats?.data?.publishedVideos || 0}</p>
          <p className="text-xs text-dark-400">Published</p>
        </div>
      </div>

      {/* CRM Status */}
      <div className="flex items-center justify-between pt-4 border-t border-dark-700">
        <div className="flex items-center gap-2">
          <Badge variant={dealer.eleadsCRM?.connected ? 'success' : 'neutral'}>
            {dealer.eleadsCRM?.connected ? 'CRM Connected' : 'CRM Not Connected'}
          </Badge>
        </div>
        <Button size="sm" variant="ghost" onClick={onSelect} icon={<ExternalLink className="w-4 h-4" />}>
          View
        </Button>
      </div>
    </Card>
  );
}

// Add Dealer Modal
function AddDealerModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    dealerId: '',
    name: '',
    csvPath: '',
  });

  const mutation = useMutation({
    mutationFn: dealerApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dealers'] });
      toast.success('Dealer added successfully');
      onClose();
      setFormData({ dealerId: '', name: '', csvPath: '' });
    },
    onError: () => toast.error('Failed to add dealer'),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(formData);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Add New Dealer">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-dark-300 mb-1">Dealer ID</label>
          <input
            type="text"
            className="input"
            placeholder="e.g., 4802"
            value={formData.dealerId}
            onChange={(e) => setFormData({ ...formData, dealerId: e.target.value })}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-dark-300 mb-1">Dealer Name</label>
          <input
            type="text"
            className="input"
            placeholder="e.g., Harley-Davidson of Dallas"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-dark-300 mb-1">CSV Feed Path</label>
          <input
            type="text"
            className="input"
            placeholder="e.g., feeds/dealer-4802.csv"
            value={formData.csvPath}
            onChange={(e) => setFormData({ ...formData, csvPath: e.target.value })}
            required
          />
        </div>
        <div className="flex justify-end gap-3 pt-4">
          <Button type="button" variant="ghost" onClick={onClose}>Cancel</Button>
          <Button type="submit" loading={mutation.isPending}>Add Dealer</Button>
        </div>
      </form>
    </Modal>
  );
}

// Dealer Settings Modal
function DealerSettingsModal({ 
  isOpen, 
  onClose, 
  dealer 
}: { 
  isOpen: boolean; 
  onClose: () => void; 
  dealer: Dealer;
}) {
  const queryClient = useQueryClient();
  const [settings, setSettings] = useState<DealerSettings>(dealer.settings);

  const mutation = useMutation({
    mutationFn: (newSettings: Partial<DealerSettings>) => 
      dealerApi.updateSettings(dealer.dealerId, newSettings),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dealers'] });
      toast.success('Settings updated');
      onClose();
    },
    onError: () => toast.error('Failed to update settings'),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(settings);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Settings: ${dealer.name}`} size="lg">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Video Duration */}
        <div>
          <label className="block text-sm font-medium text-dark-300 mb-2">Video Duration (seconds)</label>
          <div className="flex items-center gap-4">
            {[15, 30, 45, 60].map((duration) => (
              <button
                key={duration}
                type="button"
                onClick={() => setSettings({ ...settings, videoDuration: duration })}
                className={`px-4 py-2 rounded-lg border transition-colors ${
                  settings.videoDuration === duration
                    ? 'bg-primary-600 border-primary-500 text-white'
                    : 'bg-dark-700 border-dark-600 text-dark-300 hover:border-dark-500'
                }`}
              >
                {duration}s
              </button>
            ))}
          </div>
        </div>

        {/* Template */}
        <div>
          <label className="block text-sm font-medium text-dark-300 mb-2">Default Template</label>
          <select
            className="input"
            value={settings.defaultTemplate}
            onChange={(e) => setSettings({ ...settings, defaultTemplate: e.target.value })}
          >
            <option value="simple_dark">Simple Dark</option>
            <option value="modern_light">Modern Light</option>
            <option value="cinematic">Cinematic</option>
          </select>
        </div>

        {/* Resolution */}
        <div>
          <label className="block text-sm font-medium text-dark-300 mb-2">Output Resolution</label>
          <select
            className="input"
            value={settings.resolution}
            onChange={(e) => setSettings({ ...settings, resolution: e.target.value as DealerSettings['resolution'] })}
          >
            <option value="720p">720p (HD)</option>
            <option value="1080p">1080p (Full HD)</option>
            <option value="4k">4K (Ultra HD)</option>
          </select>
        </div>

        {/* Auto Approve */}
        <div className="flex items-center justify-between p-4 bg-dark-700/50 rounded-lg">
          <div>
            <p className="font-medium text-white">Auto-approve Videos</p>
            <p className="text-sm text-dark-400">Automatically approve generated videos</p>
          </div>
          <button
            type="button"
            onClick={() => setSettings({ ...settings, autoApprove: !settings.autoApprove })}
            className={`w-12 h-6 rounded-full transition-colors ${
              settings.autoApprove ? 'bg-primary-600' : 'bg-dark-600'
            }`}
          >
            <div className={`w-5 h-5 rounded-full bg-white shadow transition-transform ${
              settings.autoApprove ? 'translate-x-6' : 'translate-x-0.5'
            }`} />
          </button>
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t border-dark-700">
          <Button type="button" variant="ghost" onClick={onClose}>Cancel</Button>
          <Button type="submit" loading={mutation.isPending}>Save Settings</Button>
        </div>
      </form>
    </Modal>
  );
}

