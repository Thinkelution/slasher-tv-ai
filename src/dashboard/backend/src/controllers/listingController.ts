import { Request, Response } from 'express';
import { Listing, Script, Video } from '../models/index.js';
import { pipelineService } from '../services/PipelineService.js';
import type { ApiResponse, PaginatedResponse, IListing } from '../types/index.js';
import fs from 'fs';
import path from 'path';

export const listingController = {
  // Get all listings for a dealer
  async getByDealer(req: Request, res: Response<PaginatedResponse<IListing>>) {
    try {
      const { dealerId } = req.params;
      const page = parseInt(req.query.page as string) || 1;
      const limit = parseInt(req.query.limit as string) || 20;
      const status = req.query.status as string;

      const query: Record<string, unknown> = { dealerId };
      if (status) query.status = status;

      const total = await Listing.countDocuments(query);
      const listings = await Listing.find(query)
        .sort({ createdAt: -1 })
        .skip((page - 1) * limit)
        .limit(limit);

      res.json({
        success: true,
        data: listings,
        pagination: {
          page,
          limit,
          total,
          pages: Math.ceil(total / limit)
        }
      });
    } catch (error) {
      res.status(500).json({ 
        success: false, 
        data: [],
        pagination: { page: 1, limit: 20, total: 0, pages: 0 },
        error: (error as Error).message 
      } as unknown as PaginatedResponse<IListing>);
    }
  },

  // Get single listing
  async getById(req: Request, res: Response<ApiResponse<IListing>>) {
    try {
      const listing = await Listing.findById(req.params.id);
      if (!listing) {
        return res.status(404).json({ success: false, error: 'Listing not found' });
      }
      res.json({ success: true, data: listing });
    } catch (error) {
      res.status(500).json({ success: false, error: (error as Error).message });
    }
  },

  // Update listing photos
  async updatePhotos(req: Request, res: Response<ApiResponse<IListing>>) {
    try {
      const { id } = req.params;
      const { photoUrls, action } = req.body; // action: 'add', 'remove', 'replace'

      const listing = await Listing.findById(id);
      if (!listing) {
        return res.status(404).json({ success: false, error: 'Listing not found' });
      }

      switch (action) {
        case 'add':
          listing.photoUrls.push(...photoUrls);
          break;
        case 'remove':
          listing.photoUrls = listing.photoUrls.filter(url => !photoUrls.includes(url));
          break;
        case 'replace':
          listing.photoUrls = photoUrls;
          break;
        default:
          return res.status(400).json({ success: false, error: 'Invalid action' });
      }

      // Reset status to re-process
      listing.status = 'pending';
      await listing.save();

      res.json({ success: true, data: listing, message: 'Photos updated' });
    } catch (error) {
      res.status(400).json({ success: false, error: (error as Error).message });
    }
  },

  // Regenerate video for listing
  async regenerateVideo(req: Request, res: Response<ApiResponse<IListing>>) {
    try {
      const listing = await Listing.findById(req.params.id);
      if (!listing) {
        return res.status(404).json({ success: false, error: 'Listing not found' });
      }

      // Delete existing video
      if (listing.assets.videoPath && fs.existsSync(listing.assets.videoPath)) {
        fs.unlinkSync(listing.assets.videoPath);
      }

      // Reset status
      listing.status = 'voiceover_generated';
      listing.assets.videoPath = undefined;
      await listing.save();

      // Trigger video generation
      pipelineService.generateVideo(listing.stockNumber, listing.dealerId);

      res.json({ 
        success: true, 
        data: listing, 
        message: 'Video regeneration started' 
      });
    } catch (error) {
      res.status(500).json({ success: false, error: (error as Error).message });
    }
  },

  // Get listing assets (photos, video, QR)
  async getAssets(req: Request, res: Response) {
    try {
      const listing = await Listing.findById(req.params.id);
      if (!listing) {
        return res.status(404).json({ success: false, error: 'Listing not found' });
      }

      const script = await Script.findOne({ listingId: listing.stockNumber });
      const video = await Video.findOne({ listingId: listing.stockNumber });

      res.json({
        success: true,
        data: {
          originalPhotos: listing.assets.originalPhotos,
          processedPhotos: listing.assets.processedPhotos,
          script: script,
          voiceover: listing.assets.voiceoverPath,
          qrCode: listing.assets.qrCodePath,
          video: video
        }
      });
    } catch (error) {
      res.status(500).json({ success: false, error: (error as Error).message });
    }
  },

  // Delete listing
  async delete(req: Request, res: Response<ApiResponse<null>>) {
    try {
      const listing = await Listing.findByIdAndDelete(req.params.id);
      if (!listing) {
        return res.status(404).json({ success: false, error: 'Listing not found' });
      }

      // Clean up associated data
      await Script.deleteOne({ listingId: listing.stockNumber });
      await Video.deleteOne({ listingId: listing.stockNumber });

      res.json({ success: true, message: 'Listing deleted' });
    } catch (error) {
      res.status(500).json({ success: false, error: (error as Error).message });
    }
  }
};

