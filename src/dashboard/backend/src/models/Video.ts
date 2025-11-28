import mongoose, { Schema, Document } from 'mongoose';
import type { IVideo } from '../types/index.js';

export interface IVideoDocument extends Omit<IVideo, '_id'>, Document {}

const VideoSchema = new Schema<IVideoDocument>({
  listingId: { type: String, required: true, unique: true },
  dealerId: { type: String, required: true, index: true },
  path: { type: String, required: true },
  duration: { type: Number, required: true },
  resolution: { type: String, required: true },
  fileSize: { type: Number, required: true },
  status: { 
    type: String, 
    enum: ['processing', 'ready', 'approved', 'rejected', 'published'],
    default: 'processing'
  },
  approvedBy: { type: String },
  approvedAt: { type: Date },
  publishedAt: { type: Date },
  fastChannelId: { type: String },
  thumbnailPath: { type: String }
}, {
  timestamps: true
});

export const Video = mongoose.model<IVideoDocument>('Video', VideoSchema);

