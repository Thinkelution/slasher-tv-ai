import mongoose, { Schema, Document } from 'mongoose';
import type { IScript } from '../types/index.js';

export interface IScriptDocument extends Omit<IScript, '_id'>, Document {}

const ScriptVersionSchema = new Schema({
  content: { type: String, required: true },
  createdAt: { type: Date, default: Date.now },
  createdBy: { type: String, default: 'system' }
}, { _id: false });

const ScriptSchema = new Schema<IScriptDocument>({
  listingId: { type: String, required: true, unique: true },
  content: { type: String, required: true },
  wordCount: { type: Number, required: true },
  estimatedDuration: { type: Number, required: true },
  status: { 
    type: String, 
    enum: ['draft', 'pending_approval', 'approved', 'rejected'],
    default: 'pending_approval'
  },
  approvedBy: { type: String },
  approvedAt: { type: Date },
  rejectionReason: { type: String },
  versions: [ScriptVersionSchema]
}, {
  timestamps: true
});

export const Script = mongoose.model<IScriptDocument>('Script', ScriptSchema);

