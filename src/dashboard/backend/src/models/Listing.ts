import mongoose, { Schema, Document } from 'mongoose';
import type { IListing, ListingStatus } from '../types/index.js';

export interface IListingDocument extends Omit<IListing, '_id'>, Document {}

const ListingAssetsSchema = new Schema({
  originalPhotos: [{ type: String }],
  processedPhotos: [{ type: String }],
  script: { type: Schema.Types.ObjectId, ref: 'Script' },
  voiceoverPath: { type: String },
  qrCodePath: { type: String },
  videoPath: { type: String }
}, { _id: false });

const ListingSchema = new Schema<IListingDocument>({
  dealerId: { type: String, required: true, index: true },
  stockNumber: { type: String, required: true },
  vin: { type: String, required: true },
  year: { type: Number, required: true },
  make: { type: String, required: true },
  model: { type: String, required: true },
  trim: { type: String },
  condition: { type: String, enum: ['New', 'Used', 'Certified'], default: 'Used' },
  price: { type: Number, required: true },
  odometer: { type: Number },
  color: { type: String },
  photoUrls: [{ type: String }],
  listingUrl: { type: String, required: true },
  status: { 
    type: String, 
    enum: [
      'pending', 'images_downloaded', 'images_processed', 
      'script_generated', 'script_approved', 'voiceover_generated',
      'video_generated', 'video_approved', 'published', 'error'
    ] as ListingStatus[],
    default: 'pending'
  },
  assets: { type: ListingAssetsSchema, default: () => ({}) }
}, {
  timestamps: true
});

// Compound index for dealer + stock number
ListingSchema.index({ dealerId: 1, stockNumber: 1 }, { unique: true });

export const Listing = mongoose.model<IListingDocument>('Listing', ListingSchema);

