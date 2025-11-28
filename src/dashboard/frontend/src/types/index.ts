// ==================== DEALER ====================
export interface Dealer {
  _id: string;
  dealerId: string;
  name: string;
  csvPath: string;
  logoUrl?: string;
  settings: DealerSettings;
  eleadsCRM?: EleadsCRM;
  createdAt: string;
  updatedAt: string;
}

export interface DealerSettings {
  videoDuration: number;
  defaultTemplate: string;
  autoApprove: boolean;
  outputFormat: 'mp4' | 'webm';
  resolution: '1080p' | '720p' | '4k';
}

export interface EleadsCRM {
  connected: boolean;
  accountId?: string;
  apiKey?: string;
  lastSync?: string;
}

// ==================== LISTING ====================
export interface Listing {
  _id: string;
  dealerId: string;
  stockNumber: string;
  vin: string;
  year: number;
  make: string;
  model: string;
  trim?: string;
  condition: 'New' | 'Used' | 'Certified';
  price: number;
  odometer?: number;
  color?: string;
  photoUrls: string[];
  listingUrl: string;
  status: ListingStatus;
  assets: ListingAssets;
  createdAt: string;
  updatedAt: string;
}

export type ListingStatus = 
  | 'pending'
  | 'images_downloaded'
  | 'images_processed'
  | 'script_generated'
  | 'script_approved'
  | 'voiceover_generated'
  | 'video_generated'
  | 'video_approved'
  | 'published'
  | 'error';

export interface ListingAssets {
  originalPhotos: string[];
  processedPhotos: string[];
  script?: string;
  voiceoverPath?: string;
  qrCodePath?: string;
  videoPath?: string;
}

// ==================== SCRIPT ====================
export interface Script {
  _id: string;
  listingId: string;
  content: string;
  wordCount: number;
  estimatedDuration: number;
  status: 'draft' | 'pending_approval' | 'approved' | 'rejected';
  approvedBy?: string;
  approvedAt?: string;
  rejectionReason?: string;
  versions: ScriptVersion[];
  createdAt: string;
  updatedAt: string;
}

export interface ScriptVersion {
  content: string;
  createdAt: string;
  createdBy: string;
}

// ==================== VIDEO ====================
export interface Video {
  _id: string;
  listingId: string;
  dealerId: string;
  path: string;
  duration: number;
  resolution: string;
  fileSize: number;
  status: 'processing' | 'ready' | 'approved' | 'rejected' | 'published';
  approvedBy?: string;
  approvedAt?: string;
  publishedAt?: string;
  fastChannelId?: string;
  thumbnailPath?: string;
  createdAt: string;
  updatedAt: string;
}

// ==================== QR CODE ====================
export interface QRCode {
  listingId: string;
  url: string;
  imagePath: string;
  imageBase64?: string;
}

// ==================== API ====================
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };
}

export interface DealerStats {
  totalListings: number;
  publishedVideos: number;
  statusBreakdown: Record<string, number>;
}

