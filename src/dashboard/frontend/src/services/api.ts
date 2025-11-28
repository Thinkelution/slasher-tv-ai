import axios from 'axios';
import type { 
  Dealer, 
  DealerSettings, 
  Listing, 
  Script, 
  Video, 
  QRCode,
  ApiResponse, 
  PaginatedResponse,
  DealerStats 
} from '@/types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// ==================== DEALERS ====================
export const dealerApi = {
  getAll: () => 
    api.get<ApiResponse<Dealer[]>>('/dealers').then(r => r.data),
  
  getById: (id: string) => 
    api.get<ApiResponse<Dealer>>(`/dealers/${id}`).then(r => r.data),
  
  create: (data: Partial<Dealer>) => 
    api.post<ApiResponse<Dealer>>('/dealers', data).then(r => r.data),
  
  update: (id: string, data: Partial<Dealer>) => 
    api.put<ApiResponse<Dealer>>(`/dealers/${id}`, data).then(r => r.data),
  
  updateSettings: (id: string, settings: Partial<DealerSettings>) => 
    api.put<ApiResponse<Dealer>>(`/dealers/${id}/settings`, settings).then(r => r.data),
  
  connectCRM: (id: string, accountId: string, apiKey: string) => 
    api.post<ApiResponse<Dealer>>(`/dealers/${id}/crm/connect`, { accountId, apiKey }).then(r => r.data),
  
  delete: (id: string) => 
    api.delete<ApiResponse<null>>(`/dealers/${id}`).then(r => r.data),
  
  getStats: (id: string) => 
    api.get<ApiResponse<DealerStats>>(`/dealers/${id}/stats`).then(r => r.data),
};

// ==================== LISTINGS ====================
export const listingApi = {
  getByDealer: (dealerId: string, page = 1, limit = 20, status?: string) => 
    api.get<PaginatedResponse<Listing>>(`/dealers/${dealerId}/listings`, {
      params: { page, limit, status }
    }).then(r => r.data),
  
  getById: (id: string) => 
    api.get<ApiResponse<Listing>>(`/listings/${id}`).then(r => r.data),
  
  updatePhotos: (id: string, photoUrls: string[], action: 'add' | 'remove' | 'replace') => 
    api.put<ApiResponse<Listing>>(`/listings/${id}/photos`, { photoUrls, action }).then(r => r.data),
  
  regenerateVideo: (id: string) => 
    api.post<ApiResponse<Listing>>(`/listings/${id}/regenerate-video`).then(r => r.data),
  
  getAssets: (id: string) => 
    api.get<ApiResponse<{
      originalPhotos: string[];
      processedPhotos: string[];
      script: Script | null;
      voiceover: string | null;
      qrCode: string | null;
      video: Video | null;
    }>>(`/listings/${id}/assets`).then(r => r.data),
  
  delete: (id: string) => 
    api.delete<ApiResponse<null>>(`/listings/${id}`).then(r => r.data),
};

// ==================== SCRIPTS ====================
export const scriptApi = {
  getPending: (dealerId?: string) => 
    api.get<ApiResponse<Script[]>>('/scripts/pending', {
      params: dealerId ? { dealerId } : {}
    }).then(r => r.data),
  
  getByListing: (listingId: string) => 
    api.get<ApiResponse<Script>>(`/scripts/listing/${listingId}`).then(r => r.data),
  
  update: (id: string, content: string, editedBy?: string) => 
    api.put<ApiResponse<Script>>(`/scripts/${id}`, { content, editedBy }).then(r => r.data),
  
  approve: (id: string, approvedBy?: string) => 
    api.post<ApiResponse<Script>>(`/scripts/${id}/approve`, { approvedBy }).then(r => r.data),
  
  reject: (id: string, reason: string) => 
    api.post<ApiResponse<Script>>(`/scripts/${id}/reject`, { reason }).then(r => r.data),
  
  getVersions: (id: string) => 
    api.get<ApiResponse<{ current: string; versions: Script['versions'] }>>(`/scripts/${id}/versions`).then(r => r.data),
  
  revertVersion: (id: string, versionIndex: number) => 
    api.post<ApiResponse<Script>>(`/scripts/${id}/revert`, { versionIndex }).then(r => r.data),
};

// ==================== VIDEOS ====================
export const videoApi = {
  getByDealer: (dealerId: string, page = 1, limit = 20, status?: string) => 
    api.get<PaginatedResponse<Video>>(`/dealers/${dealerId}/videos`, {
      params: { page, limit, status }
    }).then(r => r.data),
  
  getPending: (dealerId?: string) => 
    api.get<ApiResponse<Video[]>>('/videos/pending', {
      params: dealerId ? { dealerId } : {}
    }).then(r => r.data),
  
  getById: (id: string) => 
    api.get<ApiResponse<Video>>(`/videos/${id}`).then(r => r.data),
  
  getStreamUrl: (id: string) => `/api/videos/${id}/stream`,
  
  approve: (id: string, approvedBy?: string) => 
    api.post<ApiResponse<Video>>(`/videos/${id}/approve`, { approvedBy }).then(r => r.data),
  
  reject: (id: string) => 
    api.post<ApiResponse<Video>>(`/videos/${id}/reject`).then(r => r.data),
  
  publish: (id: string, channelId?: string) => 
    api.post<ApiResponse<Video>>(`/videos/${id}/publish`, { channelId }).then(r => r.data),
  
  regenerate: (id: string) => 
    api.post<ApiResponse<Video>>(`/videos/${id}/regenerate`).then(r => r.data),
  
  delete: (id: string) => 
    api.delete<ApiResponse<null>>(`/videos/${id}`).then(r => r.data),
};

// ==================== QR CODES ====================
export const qrApi = {
  getByListing: (listingId: string) => 
    api.get<ApiResponse<QRCode>>(`/qr/listing/${listingId}`).then(r => r.data),
  
  getByDealer: (dealerId: string) => 
    api.get<ApiResponse<QRCode[]>>(`/qr/dealer/${dealerId}`).then(r => r.data),
  
  regenerate: (listingId: string) => 
    api.post<ApiResponse<QRCode>>(`/qr/${listingId}/regenerate`).then(r => r.data),
  
  getImageUrl: (listingId: string) => `/api/qr/${listingId}/image`,
  
  testScan: (listingId: string) => 
    api.get<ApiResponse<{ listingId: string; url: string; redirectTo: string }>>(`/qr/${listingId}/test`).then(r => r.data),
};

export default api;

