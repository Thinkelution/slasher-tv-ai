import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Check, X, Edit, Clock, History } from 'lucide-react';
import { Layout } from '@/components/Layout';
import { Card, CardHeader, Button, Badge, Modal } from '@/components/ui';
import { scriptApi } from '@/services/api';
import type { Script } from '@/types';
import toast from 'react-hot-toast';

export function Scripts() {
  const queryClient = useQueryClient();
  const [selectedScript, setSelectedScript] = useState<Script | null>(null);
  const [editContent, setEditContent] = useState('');
  const [showEditModal, setShowEditModal] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['scripts', 'pending'],
    queryFn: () => scriptApi.getPending(),
  });

  const approveMutation = useMutation({
    mutationFn: (id: string) => scriptApi.approve(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scripts'] });
      toast.success('Script approved');
    },
    onError: () => toast.error('Failed to approve script'),
  });

  const rejectMutation = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) => 
      scriptApi.reject(id, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scripts'] });
      toast.success('Script rejected');
    },
    onError: () => toast.error('Failed to reject script'),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, content }: { id: string; content: string }) =>
      scriptApi.update(id, content),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scripts'] });
      toast.success('Script updated');
      setShowEditModal(false);
    },
    onError: () => toast.error('Failed to update script'),
  });

  const scripts = data?.data || [];

  const handleEdit = (script: Script) => {
    setSelectedScript(script);
    setEditContent(script.content);
    setShowEditModal(true);
  };

  const handleViewHistory = (script: Script) => {
    setSelectedScript(script);
    setShowHistoryModal(true);
  };

  const handleReject = (script: Script) => {
    const reason = prompt('Enter rejection reason:');
    if (reason) {
      rejectMutation.mutate({ id: script._id, reason });
    }
  };

  return (
    <Layout title="Scripts" subtitle="Review and approve generated ad scripts">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-amber-500/20 rounded-xl">
              <Clock className="w-6 h-6 text-amber-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{scripts.length}</p>
              <p className="text-sm text-dark-400">Pending Approval</p>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-emerald-500/20 rounded-xl">
              <Check className="w-6 h-6 text-emerald-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">0</p>
              <p className="text-sm text-dark-400">Approved Today</p>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-red-500/20 rounded-xl">
              <X className="w-6 h-6 text-red-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">0</p>
              <p className="text-sm text-dark-400">Rejected Today</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Scripts List */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <div className="h-6 bg-dark-700 rounded w-1/4 mb-4" />
              <div className="h-24 bg-dark-700 rounded mb-4" />
              <div className="h-4 bg-dark-700 rounded w-1/2" />
            </Card>
          ))}
        </div>
      ) : scripts.length === 0 ? (
        <Card className="text-center py-12">
          <Check className="w-12 h-12 text-emerald-400 mx-auto mb-4" />
          <p className="text-lg font-medium text-white mb-2">All caught up!</p>
          <p className="text-dark-400">No scripts pending approval</p>
        </Card>
      ) : (
        <div className="space-y-4">
          {scripts.map((script) => (
            <ScriptCard
              key={script._id}
              script={script}
              onApprove={() => approveMutation.mutate(script._id)}
              onReject={() => handleReject(script)}
              onEdit={() => handleEdit(script)}
              onViewHistory={() => handleViewHistory(script)}
              isApproving={approveMutation.isPending}
            />
          ))}
        </div>
      )}

      {/* Edit Modal */}
      {selectedScript && (
        <Modal
          isOpen={showEditModal}
          onClose={() => setShowEditModal(false)}
          title="Edit Script"
          size="lg"
        >
          <div className="space-y-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-dark-400">Listing: {selectedScript.listingId}</span>
              <span className="text-dark-400">
                {editContent.split(/\s+/).length} words • ~{Math.ceil(editContent.split(/\s+/).length / 2.5)}s
              </span>
            </div>
            <textarea
              className="input min-h-[200px] font-mono text-sm"
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
            />
            <div className="flex justify-end gap-3">
              <Button variant="ghost" onClick={() => setShowEditModal(false)}>
                Cancel
              </Button>
              <Button
                onClick={() => updateMutation.mutate({ id: selectedScript._id, content: editContent })}
                loading={updateMutation.isPending}
              >
                Save Changes
              </Button>
            </div>
          </div>
        </Modal>
      )}

      {/* History Modal */}
      {selectedScript && (
        <ScriptHistoryModal
          isOpen={showHistoryModal}
          onClose={() => setShowHistoryModal(false)}
          script={selectedScript}
        />
      )}
    </Layout>
  );
}

// Script Card Component
function ScriptCard({
  script,
  onApprove,
  onReject,
  onEdit,
  onViewHistory,
  isApproving,
}: {
  script: Script;
  onApprove: () => void;
  onReject: () => void;
  onEdit: () => void;
  onViewHistory: () => void;
  isApproving: boolean;
}) {
  return (
    <Card>
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="font-semibold text-white">Listing: {script.listingId}</h3>
          <div className="flex items-center gap-3 mt-1">
            <Badge variant="warning">Pending Approval</Badge>
            <span className="text-sm text-dark-400">{script.wordCount} words</span>
            <span className="text-sm text-dark-400">~{script.estimatedDuration}s</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button size="sm" variant="ghost" onClick={onViewHistory} icon={<History className="w-4 h-4" />}>
            History
          </Button>
          <Button size="sm" variant="ghost" onClick={onEdit} icon={<Edit className="w-4 h-4" />}>
            Edit
          </Button>
        </div>
      </div>

      {/* Script Content */}
      <div className="p-4 bg-dark-700/50 rounded-lg mb-4">
        <p className="text-dark-200 whitespace-pre-wrap leading-relaxed">{script.content}</p>
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between pt-4 border-t border-dark-700">
        <p className="text-sm text-dark-400">
          Generated {new Date(script.createdAt).toLocaleDateString()}
        </p>
        <div className="flex items-center gap-3">
          <Button 
            variant="danger" 
            size="sm" 
            onClick={onReject}
            icon={<X className="w-4 h-4" />}
          >
            Reject
          </Button>
          <Button 
            size="sm" 
            onClick={onApprove}
            loading={isApproving}
            icon={<Check className="w-4 h-4" />}
          >
            Approve
          </Button>
        </div>
      </div>
    </Card>
  );
}

// Script History Modal
function ScriptHistoryModal({
  isOpen,
  onClose,
  script,
}: {
  isOpen: boolean;
  onClose: () => void;
  script: Script;
}) {
  const queryClient = useQueryClient();
  
  const { data } = useQuery({
    queryKey: ['script-versions', script._id],
    queryFn: () => scriptApi.getVersions(script._id),
    enabled: isOpen,
  });

  const revertMutation = useMutation({
    mutationFn: (versionIndex: number) => scriptApi.revertVersion(script._id, versionIndex),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scripts'] });
      toast.success('Reverted to previous version');
      onClose();
    },
    onError: () => toast.error('Failed to revert'),
  });

  const versions = data?.data?.versions || [];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Script History" size="lg">
      <div className="space-y-4 max-h-[60vh] overflow-y-auto">
        {/* Current Version */}
        <div className="p-4 bg-primary-600/10 border border-primary-500/30 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <Badge variant="info">Current Version</Badge>
            <span className="text-xs text-dark-400">Now</span>
          </div>
          <p className="text-sm text-dark-200 whitespace-pre-wrap">{data?.data?.current}</p>
        </div>

        {/* Previous Versions */}
        {versions.length === 0 ? (
          <p className="text-center text-dark-400 py-4">No previous versions</p>
        ) : (
          versions.map((version, index) => (
            <div key={index} className="p-4 bg-dark-700/50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-dark-400">
                  Edited by {version.createdBy}
                </span>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-dark-400">
                    {new Date(version.createdAt).toLocaleString()}
                  </span>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => revertMutation.mutate(index)}
                    loading={revertMutation.isPending}
                  >
                    Revert
                  </Button>
                </div>
              </div>
              <p className="text-sm text-dark-300 whitespace-pre-wrap">{version.content}</p>
            </div>
          ))
        )}
      </div>
    </Modal>
  );
}

