import { Request, Response } from 'express';
import { Video, Listing } from '../models/index.js';
import { pipelineService } from '../services/PipelineService.js';
import type { ApiResponse, PaginatedResponse, IVideo } from '../types/index.js';
import fs from 'fs';
import path from 'path';

export const videoController = {
  // Get all videos for a dealer
  async getByDealer(req: Request, res: Response<PaginatedResponse<IVideo>>) {
    try {
      const { dealerId } = req.params;
      const page = parseInt(req.query.page as string) || 1;
      const limit = parseInt(req.query.limit as string) || 20;
      const status = req.query.status as string;

      const query: Record<string, unknown> = { dealerId };
      if (status) query.status = status;

      const total = await Video.countDocuments(query);
      const videos = await Video.find(query)
        .sort({ createdAt: -1 })
        .skip((page - 1) * limit)
        .limit(limit);

      res.json({
        success: true,
        data: videos,
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
        pagination: { page: 1, limit: 20, total: 0, pages: 0 }
      } as PaginatedResponse<IVideo>);
    }
  },

  // Get videos pending approval
  async getPendingApproval(req: Request, res: Response<ApiResponse<IVideo[]>>) {
    try {
      const dealerId = req.query.dealerId as string;
      
      const query: Record<string, unknown> = { status: 'ready' };
      if (dealerId) query.dealerId = dealerId;

      const videos = await Video.find(query).sort({ createdAt: -1 });
      res.json({ success: true, data: videos });
    } catch (error) {
      res.status(500).json({ success: false, error: (error as Error).message });
    }
  },

  // Get single video
  async getById(req: Request, res: Response<ApiResponse<IVideo>>) {
    try {
      const video = await Video.findById(req.params.id);
      if (!video) {
        return res.status(404).json({ success: false, error: 'Video not found' });
      }
      res.json({ success: true, data: video });
    } catch (error) {
      res.status(500).json({ success: false, error: (error as Error).message });
    }
  },

  // Approve video
  async approve(req: Request, res: Response<ApiResponse<IVideo>>) {
    try {
      const video = await Video.findByIdAndUpdate(
        req.params.id,
        {
          status: 'approved',
          approvedBy: req.body.approvedBy || 'admin',
          approvedAt: new Date()
        },
        { new: true }
      );

      if (!video) {
        return res.status(404).json({ success: false, error: 'Video not found' });
      }

      // Update listing status
      await Listing.findOneAndUpdate(
        { stockNumber: video.listingId },
        { status: 'video_approved' }
      );

      res.json({ success: true, data: video, message: 'Video approved' });
    } catch (error) {
      res.status(400).json({ success: false, error: (error as Error).message });
    }
  },

  // Reject video
  async reject(req: Request, res: Response<ApiResponse<IVideo>>) {
    try {
      const video = await Video.findByIdAndUpdate(
        req.params.id,
        { status: 'rejected' },
        { new: true }
      );

      if (!video) {
        return res.status(404).json({ success: false, error: 'Video not found' });
      }

      res.json({ success: true, data: video, message: 'Video rejected' });
    } catch (error) {
      res.status(400).json({ success: false, error: (error as Error).message });
    }
  },

  // Publish video to FAST channel
  async publish(req: Request, res: Response<ApiResponse<IVideo>>) {
    try {
      const video = await Video.findById(req.params.id);
      
      if (!video) {
        return res.status(404).json({ success: false, error: 'Video not found' });
      }

      if (video.status !== 'approved') {
        return res.status(400).json({ 
          success: false, 
          error: 'Video must be approved before publishing' 
        });
      }

      // TODO: Integrate with FAST channel API
      video.status = 'published';
      video.publishedAt = new Date();
      video.fastChannelId = req.body.channelId;
      await video.save();

      // Update listing status
      await Listing.findOneAndUpdate(
        { stockNumber: video.listingId },
        { status: 'published' }
      );

      res.json({ success: true, data: video, message: 'Video published' });
    } catch (error) {
      res.status(400).json({ success: false, error: (error as Error).message });
    }
  },

  // Regenerate video
  async regenerate(req: Request, res: Response<ApiResponse<IVideo>>) {
    try {
      const video = await Video.findById(req.params.id);
      
      if (!video) {
        return res.status(404).json({ success: false, error: 'Video not found' });
      }

      // Delete existing video file
      if (fs.existsSync(video.path)) {
        fs.unlinkSync(video.path);
      }

      // Reset status
      video.status = 'processing';
      await video.save();

      // Trigger regeneration
      pipelineService.generateVideo(video.listingId, video.dealerId);

      res.json({ success: true, data: video, message: 'Video regeneration started' });
    } catch (error) {
      res.status(500).json({ success: false, error: (error as Error).message });
    }
  },

  // Stream video file
  async stream(req: Request, res: Response) {
    try {
      const video = await Video.findById(req.params.id);
      
      if (!video) {
        return res.status(404).json({ success: false, error: 'Video not found' });
      }

      if (!fs.existsSync(video.path)) {
        return res.status(404).json({ success: false, error: 'Video file not found' });
      }

      const stat = fs.statSync(video.path);
      const fileSize = stat.size;
      const range = req.headers.range;

      if (range) {
        const parts = range.replace(/bytes=/, '').split('-');
        const start = parseInt(parts[0], 10);
        const end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;
        const chunksize = end - start + 1;
        const file = fs.createReadStream(video.path, { start, end });
        
        res.writeHead(206, {
          'Content-Range': `bytes ${start}-${end}/${fileSize}`,
          'Accept-Ranges': 'bytes',
          'Content-Length': chunksize,
          'Content-Type': 'video/mp4'
        });
        
        file.pipe(res);
      } else {
        res.writeHead(200, {
          'Content-Length': fileSize,
          'Content-Type': 'video/mp4'
        });
        fs.createReadStream(video.path).pipe(res);
      }
    } catch (error) {
      res.status(500).json({ success: false, error: (error as Error).message });
    }
  },

  // Delete video
  async delete(req: Request, res: Response<ApiResponse<null>>) {
    try {
      const video = await Video.findByIdAndDelete(req.params.id);
      
      if (!video) {
        return res.status(404).json({ success: false, error: 'Video not found' });
      }

      // Delete file
      if (fs.existsSync(video.path)) {
        fs.unlinkSync(video.path);
      }

      // Update listing
      await Listing.findOneAndUpdate(
        { stockNumber: video.listingId },
        { 
          status: 'voiceover_generated',
          'assets.videoPath': null
        }
      );

      res.json({ success: true, message: 'Video deleted' });
    } catch (error) {
      res.status(500).json({ success: false, error: (error as Error).message });
    }
  }
};

