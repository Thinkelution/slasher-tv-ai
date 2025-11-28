import mongoose, { Schema, Document } from 'mongoose';
import type { IJob, JobType } from '../types/index.js';

export interface IJobDocument extends Omit<IJob, '_id'>, Document {}

const JobSchema = new Schema<IJobDocument>({
  type: { 
    type: String, 
    enum: [
      'import_csv', 'download_images', 'process_images',
      'generate_script', 'generate_voiceover', 'generate_video',
      'regenerate_video', 'publish_video'
    ] as JobType[],
    required: true
  },
  dealerId: { type: String, required: true, index: true },
  listingId: { type: String },
  status: { 
    type: String, 
    enum: ['queued', 'processing', 'completed', 'failed'],
    default: 'queued'
  },
  progress: { type: Number, default: 0 },
  error: { type: String },
  startedAt: { type: Date },
  completedAt: { type: Date }
}, {
  timestamps: true
});

export const Job = mongoose.model<IJobDocument>('Job', JobSchema);

