// ==================== DEALER ====================
export interface IDealer {
  _id?: string;
  dealerId: string;
  name: string;
  csvPath: string;
  logoUrl?: string;
  settings: IDealerSettings;
  eleadsCRM?: IEleadsCRM;
  createdAt?: Date;
  updatedAt?: Date;
}

export interface IDealerSettings {
  videoDuration: number; // seconds (default 30)
  defaultTemplate: string;
  autoApprove: boolean;
  outputFormat: 'mp4' | 'webm';
  resolution: '1080p' | '720p' | '4k';
}

export interface IEleadsCRM {
  connected: boolean;
  accountId?: string;
  apiKey?: string;
  lastSync?: Date;
}

// ==================== LISTING ====================
export interface IListing {
  _id?: string;
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
  assets: IListingAssets;
  createdAt?: Date;
  updatedAt?: Date;
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

export interface IListingAssets {
  originalPhotos: string[];
  processedPhotos: string[];
  script?: IScript;
  voiceoverPath?: string;
  qrCodePath?: string;
  videoPath?: string;
}

// ==================== SCRIPT ====================
export interface IScript {
  _id?: string;
  listingId: string;
  content: string;
  wordCount: number;
  estimatedDuration: number; // seconds
  status: 'draft' | 'pending_approval' | 'approved' | 'rejected';
  approvedBy?: string;
  approvedAt?: Date;
  rejectionReason?: string;
  versions: IScriptVersion[];
  createdAt?: Date;
  updatedAt?: Date;
}

export interface IScriptVersion {
  content: string;
  createdAt: Date;
  createdBy: string;
}

// ==================== VIDEO ====================
export interface IVideo {
  _id?: string;
  listingId: string;
  dealerId: string;
  path: string;
  duration: number;
  resolution: string;
  fileSize: number;
  status: 'processing' | 'ready' | 'approved' | 'rejected' | 'published';
  approvedBy?: string;
  approvedAt?: Date;
  publishedAt?: Date;
  fastChannelId?: string;
  thumbnailPath?: string;
  createdAt?: Date;
  updatedAt?: Date;
}

// ==================== QR CODE ====================
export interface IQRCode {
  _id?: string;
  listingId: string;
  url: string;
  imagePath: string;
  scans: number;
  lastScanned?: Date;
  createdAt?: Date;
}

// ==================== FAST CHANNEL ====================
export interface IFastChannel {
  _id?: string;
  dealerId: string;
  name: string;
  playlistUrl: string;
  videos: string[]; // video IDs
  status: 'active' | 'paused' | 'offline';
  lastUpdated?: Date;
}

// ==================== JOB QUEUE ====================
export interface IJob {
  _id?: string;
  type: JobType;
  dealerId: string;
  listingId?: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number;
  error?: string;
  startedAt?: Date;
  completedAt?: Date;
  createdAt?: Date;
}

export type JobType = 
  | 'import_csv'
  | 'download_images'
  | 'process_images'
  | 'generate_script'
  | 'generate_voiceover'
  | 'generate_video'
  | 'regenerate_video'
  | 'publish_video';

// ==================== API RESPONSES ====================
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

