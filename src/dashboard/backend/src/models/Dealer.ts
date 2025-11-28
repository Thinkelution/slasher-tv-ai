import mongoose, { Schema, Document } from 'mongoose';
import type { IDealer } from '../types/index.js';

export interface IDealerDocument extends Omit<IDealer, '_id'>, Document {}

const DealerSettingsSchema = new Schema({
  videoDuration: { type: Number, default: 30 },
  defaultTemplate: { type: String, default: 'simple_dark' },
  autoApprove: { type: Boolean, default: false },
  outputFormat: { type: String, enum: ['mp4', 'webm'], default: 'mp4' },
  resolution: { type: String, enum: ['1080p', '720p', '4k'], default: '1080p' }
}, { _id: false });

const EleadsCRMSchema = new Schema({
  connected: { type: Boolean, default: false },
  accountId: { type: String },
  apiKey: { type: String },
  lastSync: { type: Date }
}, { _id: false });

const DealerSchema = new Schema<IDealerDocument>({
  dealerId: { type: String, required: true, unique: true },
  name: { type: String, required: true },
  csvPath: { type: String, required: true },
  logoUrl: { type: String },
  settings: { type: DealerSettingsSchema, default: () => ({}) },
  eleadsCRM: { type: EleadsCRMSchema, default: () => ({}) }
}, {
  timestamps: true
});

export const Dealer = mongoose.model<IDealerDocument>('Dealer', DealerSchema);

