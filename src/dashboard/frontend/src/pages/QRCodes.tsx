import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { QrCode, RefreshCw, ExternalLink, Download, Search } from 'lucide-react';
import { Layout } from '@/components/Layout';
import { Card, CardHeader, Button, Modal } from '@/components/ui';
import { qrApi, dealerApi } from '@/services/api';
import type { QRCode } from '@/types';
import toast from 'react-hot-toast';

export function QRCodes() {
  const queryClient = useQueryClient();
  const [selectedDealer, setSelectedDealer] = useState<string>('');
  const [selectedQR, setSelectedQR] = useState<QRCode | null>(null);
  const [showTestModal, setShowTestModal] = useState(false);

  const { data: dealers } = useQuery({
    queryKey: ['dealers'],
    queryFn: dealerApi.getAll,
  });

  const { data: qrCodes, isLoading } = useQuery({
    queryKey: ['qr-codes', selectedDealer],
    queryFn: () => qrApi.getByDealer(selectedDealer),
    enabled: !!selectedDealer,
  });

  const regenerateMutation = useMutation({
    mutationFn: (listingId: string) => qrApi.regenerate(listingId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['qr-codes'] });
      toast.success('QR code regenerated');
    },
    onError: () => toast.error('Failed to regenerate QR code'),
  });

  const testMutation = useMutation({
    mutationFn: (listingId: string) => qrApi.testScan(listingId),
    onSuccess: (data) => {
      if (data.data) {
        toast.success(`QR code is valid! Redirects to: ${data.data.url}`);
      }
    },
    onError: () => toast.error('QR code test failed'),
  });

  const codes = qrCodes?.data || [];
  const dealerList = dealers?.data || [];

  const handleTest = (qr: QRCode) => {
    setSelectedQR(qr);
    setShowTestModal(true);
  };

  const handleDownload = (qr: QRCode) => {
    const link = document.createElement('a');
    link.href = qrApi.getImageUrl(qr.listingId);
    link.download = `qr-${qr.listingId}.png`;
    link.click();
  };

  return (
    <Layout title="QR Codes" subtitle="View and test QR codes for all listings">
      {/* Dealer Selector */}
      <Card className="mb-6">
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium text-dark-300">Select Dealer:</label>
          <select
            className="input max-w-xs"
            value={selectedDealer}
            onChange={(e) => setSelectedDealer(e.target.value)}
          >
            <option value="">Choose a dealer...</option>
            {dealerList.map((dealer) => (
              <option key={dealer._id} value={dealer.dealerId}>
                {dealer.name}
              </option>
            ))}
          </select>
        </div>
      </Card>

      {/* QR Codes Grid */}
      {!selectedDealer ? (
        <Card className="text-center py-12">
          <QrCode className="w-12 h-12 text-dark-500 mx-auto mb-4" />
          <p className="text-lg font-medium text-white mb-2">Select a Dealer</p>
          <p className="text-dark-400">Choose a dealer to view their QR codes</p>
        </Card>
      ) : isLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
          {[1, 2, 3, 4, 5].map((i) => (
            <Card key={i} className="animate-pulse">
              <div className="aspect-square bg-dark-700 rounded-lg mb-4" />
              <div className="h-4 bg-dark-700 rounded w-3/4" />
            </Card>
          ))}
        </div>
      ) : codes.length === 0 ? (
        <Card className="text-center py-12">
          <QrCode className="w-12 h-12 text-dark-500 mx-auto mb-4" />
          <p className="text-lg font-medium text-white mb-2">No QR Codes Found</p>
          <p className="text-dark-400">QR codes will be generated with videos</p>
        </Card>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
          {codes.map((qr) => (
            <QRCodeCard
              key={qr.listingId}
              qr={qr}
              onTest={() => handleTest(qr)}
              onRegenerate={() => regenerateMutation.mutate(qr.listingId)}
              onDownload={() => handleDownload(qr)}
              isRegenerating={regenerateMutation.isPending}
            />
          ))}
        </div>
      )}

      {/* Test Modal */}
      {selectedQR && (
        <QRTestModal
          isOpen={showTestModal}
          onClose={() => {
            setShowTestModal(false);
            setSelectedQR(null);
          }}
          qr={selectedQR}
          onTest={() => testMutation.mutate(selectedQR.listingId)}
          isTesting={testMutation.isPending}
        />
      )}
    </Layout>
  );
}

// QR Code Card Component
function QRCodeCard({
  qr,
  onTest,
  onRegenerate,
  onDownload,
  isRegenerating,
}: {
  qr: QRCode;
  onTest: () => void;
  onRegenerate: () => void;
  onDownload: () => void;
  isRegenerating: boolean;
}) {
  return (
    <Card className="group">
      {/* QR Image */}
      <div 
        className="relative aspect-square bg-white rounded-lg mb-4 p-4 cursor-pointer"
        onClick={onTest}
      >
        {qr.imageBase64 ? (
          <img 
            src={qr.imageBase64} 
            alt={`QR code for ${qr.listingId}`}
            className="w-full h-full object-contain"
          />
        ) : (
          <img 
            src={qrApi.getImageUrl(qr.listingId)} 
            alt={`QR code for ${qr.listingId}`}
            className="w-full h-full object-contain"
          />
        )}
        
        {/* Hover overlay */}
        <div className="absolute inset-0 bg-dark-900/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center rounded-lg">
          <Button size="sm" variant="secondary" icon={<Search className="w-4 h-4" />}>
            Test
          </Button>
        </div>
      </div>

      {/* Info */}
      <div className="mb-3">
        <p className="font-medium text-white truncate">#{qr.listingId}</p>
        <p className="text-xs text-dark-400 truncate" title={qr.url}>
          {qr.url}
        </p>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        <Button 
          size="sm" 
          variant="ghost" 
          onClick={onDownload}
          className="flex-1"
          icon={<Download className="w-4 h-4" />}
        >
          Save
        </Button>
        <Button 
          size="sm" 
          variant="ghost" 
          onClick={onRegenerate}
          disabled={isRegenerating}
          icon={<RefreshCw className={`w-4 h-4 ${isRegenerating ? 'animate-spin' : ''}`} />}
        />
      </div>
    </Card>
  );
}

// QR Test Modal
function QRTestModal({
  isOpen,
  onClose,
  qr,
  onTest,
  isTesting,
}: {
  isOpen: boolean;
  onClose: () => void;
  qr: QRCode;
  onTest: () => void;
  isTesting: boolean;
}) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Test QR Code" size="md">
      <div className="space-y-6">
        {/* Large QR Display */}
        <div className="flex justify-center">
          <div className="w-64 h-64 bg-white rounded-xl p-4">
            {qr.imageBase64 ? (
              <img 
                src={qr.imageBase64} 
                alt="QR Code"
                className="w-full h-full object-contain"
              />
            ) : (
              <img 
                src={qrApi.getImageUrl(qr.listingId)} 
                alt="QR Code"
                className="w-full h-full object-contain"
              />
            )}
          </div>
        </div>

        {/* Info */}
        <div className="space-y-2">
          <div className="flex items-center justify-between p-3 bg-dark-700/50 rounded-lg">
            <span className="text-sm text-dark-400">Listing ID</span>
            <span className="font-mono text-white">{qr.listingId}</span>
          </div>
          <div className="flex items-center justify-between p-3 bg-dark-700/50 rounded-lg">
            <span className="text-sm text-dark-400">Destination URL</span>
            <a 
              href={qr.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-primary-400 hover:text-primary-300 transition-colors"
            >
              <span className="truncate max-w-[200px]">{qr.url}</span>
              <ExternalLink className="w-4 h-4 flex-shrink-0" />
            </a>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3">
          <Button variant="ghost" onClick={onClose}>Close</Button>
          <Button 
            onClick={onTest}
            loading={isTesting}
            icon={<Search className="w-4 h-4" />}
          >
            Verify QR Code
          </Button>
          <a 
            href={qr.url} 
            target="_blank" 
            rel="noopener noreferrer"
          >
            <Button variant="secondary" icon={<ExternalLink className="w-4 h-4" />}>
              Open URL
            </Button>
          </a>
        </div>
      </div>
    </Modal>
  );
}

