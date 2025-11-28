import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Check, X, Play, RefreshCw, Upload, Eye } from 'lucide-react';
import { Layout } from '@/components/Layout';
import { Card, CardHeader, Button, Badge, Modal } from '@/components/ui';
import { videoApi } from '@/services/api';
import type { Video } from '@/types';
import toast from 'react-hot-toast';
import clsx from 'clsx';

export function Videos() {
  const queryClient = useQueryClient();
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null);
  const [showPreviewModal, setShowPreviewModal] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['videos', 'pending'],
    queryFn: () => videoApi.getPending(),
  });

  const approveMutation = useMutation({
    mutationFn: (id: string) => videoApi.approve(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['videos'] });
      toast.success('Video approved');
    },
    onError: () => toast.error('Failed to approve video'),
  });

  const rejectMutation = useMutation({
    mutationFn: (id: string) => videoApi.reject(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['videos'] });
      toast.success('Video rejected');
    },
    onError: () => toast.error('Failed to reject video'),
  });

  const regenerateMutation = useMutation({
    mutationFn: (id: string) => videoApi.regenerate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['videos'] });
      toast.success('Video regeneration started');
    },
    onError: () => toast.error('Failed to regenerate video'),
  });

  const publishMutation = useMutation({
    mutationFn: (id: string) => videoApi.publish(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['videos'] });
      toast.success('Video published');
    },
    onError: () => toast.error('Failed to publish video'),
  });

  const videos = data?.data || [];

  const handlePreview = (video: Video) => {
    setSelectedVideo(video);
    setShowPreviewModal(true);
  };

  return (
    <Layout title="Videos" subtitle="Review and approve generated videos before publishing">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card>
          <div className="text-center">
            <p className="text-3xl font-bold text-white">{videos.length}</p>
            <p className="text-sm text-dark-400">Pending Review</p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <p className="text-3xl font-bold text-emerald-400">0</p>
            <p className="text-sm text-dark-400">Approved</p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <p className="text-3xl font-bold text-purple-400">0</p>
            <p className="text-sm text-dark-400">Published</p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <p className="text-3xl font-bold text-amber-400">0</p>
            <p className="text-sm text-dark-400">Processing</p>
          </div>
        </Card>
      </div>

      {/* Videos Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <div className="aspect-video bg-dark-700 rounded-lg mb-4" />
              <div className="h-4 bg-dark-700 rounded w-3/4 mb-2" />
              <div className="h-4 bg-dark-700 rounded w-1/2" />
            </Card>
          ))}
        </div>
      ) : videos.length === 0 ? (
        <Card className="text-center py-12">
          <Play className="w-12 h-12 text-dark-500 mx-auto mb-4" />
          <p className="text-lg font-medium text-white mb-2">No videos to review</p>
          <p className="text-dark-400">Videos will appear here once generated</p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {videos.map((video) => (
            <VideoCard
              key={video._id}
              video={video}
              onPreview={() => handlePreview(video)}
              onApprove={() => approveMutation.mutate(video._id)}
              onReject={() => rejectMutation.mutate(video._id)}
              onRegenerate={() => regenerateMutation.mutate(video._id)}
              onPublish={() => publishMutation.mutate(video._id)}
              isLoading={approveMutation.isPending || rejectMutation.isPending}
            />
          ))}
        </div>
      )}

      {/* Preview Modal */}
      {selectedVideo && (
        <VideoPreviewModal
          isOpen={showPreviewModal}
          onClose={() => {
            setShowPreviewModal(false);
            setSelectedVideo(null);
          }}
          video={selectedVideo}
          onApprove={() => {
            approveMutation.mutate(selectedVideo._id);
            setShowPreviewModal(false);
          }}
          onReject={() => {
            rejectMutation.mutate(selectedVideo._id);
            setShowPreviewModal(false);
          }}
        />
      )}
    </Layout>
  );
}

// Video Card Component
function VideoCard({
  video,
  onPreview,
  onApprove,
  onReject,
  onRegenerate,
  onPublish,
  isLoading,
}: {
  video: Video;
  onPreview: () => void;
  onApprove: () => void;
  onReject: () => void;
  onRegenerate: () => void;
  onPublish: () => void;
  isLoading: boolean;
}) {
  const statusColors = {
    processing: 'text-amber-400',
    ready: 'text-blue-400',
    approved: 'text-emerald-400',
    rejected: 'text-red-400',
    published: 'text-purple-400',
  };

  return (
    <Card className="group">
      {/* Thumbnail */}
      <div 
        className="relative aspect-video bg-dark-700 rounded-lg mb-4 overflow-hidden cursor-pointer"
        onClick={onPreview}
      >
        {video.thumbnailPath ? (
          <img 
            src={`/assets/${video.thumbnailPath}`} 
            alt="Video thumbnail"
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Play className="w-12 h-12 text-dark-500" />
          </div>
        )}
        
        {/* Overlay */}
        <div className="absolute inset-0 bg-dark-900/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
          <Button variant="secondary" icon={<Eye className="w-4 h-4" />}>
            Preview
          </Button>
        </div>

        {/* Duration badge */}
        <div className="absolute bottom-2 right-2 px-2 py-1 bg-dark-900/80 rounded text-xs text-white">
          {Math.floor(video.duration)}s
        </div>
      </div>

      {/* Info */}
      <div className="mb-4">
        <h3 className="font-semibold text-white truncate">Listing: {video.listingId}</h3>
        <div className="flex items-center gap-3 mt-1">
          <Badge 
            variant={
              video.status === 'approved' ? 'success' :
              video.status === 'rejected' ? 'error' :
              video.status === 'published' ? 'info' : 'warning'
            }
          >
            {video.status.charAt(0).toUpperCase() + video.status.slice(1)}
          </Badge>
          <span className="text-sm text-dark-400">{video.resolution}</span>
          <span className="text-sm text-dark-400">
            {(video.fileSize / 1024 / 1024).toFixed(1)} MB
          </span>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 pt-4 border-t border-dark-700">
        {video.status === 'ready' && (
          <>
            <Button 
              size="sm" 
              variant="danger" 
              onClick={onReject}
              disabled={isLoading}
              className="flex-1"
            >
              <X className="w-4 h-4" />
            </Button>
            <Button 
              size="sm" 
              onClick={onApprove}
              disabled={isLoading}
              className="flex-1"
            >
              <Check className="w-4 h-4" />
            </Button>
          </>
        )}
        {video.status === 'approved' && (
          <Button 
            size="sm" 
            onClick={onPublish}
            className="flex-1"
            icon={<Upload className="w-4 h-4" />}
          >
            Publish
          </Button>
        )}
        {(video.status === 'rejected' || video.status === 'ready') && (
          <Button 
            size="sm" 
            variant="ghost" 
            onClick={onRegenerate}
            icon={<RefreshCw className="w-4 h-4" />}
          >
            Regenerate
          </Button>
        )}
      </div>
    </Card>
  );
}

// Video Preview Modal
function VideoPreviewModal({
  isOpen,
  onClose,
  video,
  onApprove,
  onReject,
}: {
  isOpen: boolean;
  onClose: () => void;
  video: Video;
  onApprove: () => void;
  onReject: () => void;
}) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Video Preview" size="xl">
      <div className="space-y-4">
        {/* Video Player */}
        <div className="video-player">
          <video 
            controls 
            autoPlay
            src={videoApi.getStreamUrl(video._id)}
            className="w-full h-full"
          >
            Your browser does not support the video tag.
          </video>
        </div>

        {/* Video Info */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-3 bg-dark-700/50 rounded-lg">
            <p className="text-xs text-dark-400">Duration</p>
            <p className="font-semibold text-white">{video.duration}s</p>
          </div>
          <div className="p-3 bg-dark-700/50 rounded-lg">
            <p className="text-xs text-dark-400">Resolution</p>
            <p className="font-semibold text-white">{video.resolution}</p>
          </div>
          <div className="p-3 bg-dark-700/50 rounded-lg">
            <p className="text-xs text-dark-400">File Size</p>
            <p className="font-semibold text-white">{(video.fileSize / 1024 / 1024).toFixed(1)} MB</p>
          </div>
          <div className="p-3 bg-dark-700/50 rounded-lg">
            <p className="text-xs text-dark-400">Created</p>
            <p className="font-semibold text-white">
              {new Date(video.createdAt).toLocaleDateString()}
            </p>
          </div>
        </div>

        {/* Actions */}
        {video.status === 'ready' && (
          <div className="flex justify-end gap-3 pt-4 border-t border-dark-700">
            <Button variant="danger" onClick={onReject} icon={<X className="w-4 h-4" />}>
              Reject
            </Button>
            <Button onClick={onApprove} icon={<Check className="w-4 h-4" />}>
              Approve
            </Button>
          </div>
        )}
      </div>
    </Modal>
  );
}

