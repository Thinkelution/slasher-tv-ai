import { Request, Response } from 'express';
import { Dealer } from '../models/index.js';
import { Listing } from '../models/index.js';
import type { ApiResponse, IDealer } from '../types/index.js';

export const dealerController = {
  // Get all dealers
  async getAll(req: Request, res: Response<ApiResponse<IDealer[]>>) {
    try {
      const dealers = await Dealer.find().sort({ createdAt: -1 });
      res.json({ success: true, data: dealers });
    } catch (error) {
      res.status(500).json({ success: false, error: (error as Error).message });
    }
  },

  // Get dealer by ID
  async getById(req: Request, res: Response<ApiResponse<IDealer>>) {
    try {
      const dealer = await Dealer.findOne({ dealerId: req.params.id });
      if (!dealer) {
        return res.status(404).json({ success: false, error: 'Dealer not found' });
      }
      res.json({ success: true, data: dealer });
    } catch (error) {
      res.status(500).json({ success: false, error: (error as Error).message });
    }
  },

  // Create dealer
  async create(req: Request, res: Response<ApiResponse<IDealer>>) {
    try {
      const dealer = new Dealer(req.body);
      await dealer.save();
      res.status(201).json({ success: true, data: dealer });
    } catch (error) {
      res.status(400).json({ success: false, error: (error as Error).message });
    }
  },

  // Update dealer
  async update(req: Request, res: Response<ApiResponse<IDealer>>) {
    try {
      const dealer = await Dealer.findOneAndUpdate(
        { dealerId: req.params.id },
        req.body,
        { new: true, runValidators: true }
      );
      if (!dealer) {
        return res.status(404).json({ success: false, error: 'Dealer not found' });
      }
      res.json({ success: true, data: dealer });
    } catch (error) {
      res.status(400).json({ success: false, error: (error as Error).message });
    }
  },

  // Update dealer settings
  async updateSettings(req: Request, res: Response<ApiResponse<IDealer>>) {
    try {
      const dealer = await Dealer.findOneAndUpdate(
        { dealerId: req.params.id },
        { $set: { settings: req.body } },
        { new: true, runValidators: true }
      );
      if (!dealer) {
        return res.status(404).json({ success: false, error: 'Dealer not found' });
      }
      res.json({ success: true, data: dealer, message: 'Settings updated' });
    } catch (error) {
      res.status(400).json({ success: false, error: (error as Error).message });
    }
  },

  // Connect Eleads CRM
  async connectEleadsCRM(req: Request, res: Response<ApiResponse<IDealer>>) {
    try {
      const { accountId, apiKey } = req.body;
      
      // TODO: Validate CRM credentials with Eleads API
      
      const dealer = await Dealer.findOneAndUpdate(
        { dealerId: req.params.id },
        { 
          $set: { 
            'eleadsCRM.connected': true,
            'eleadsCRM.accountId': accountId,
            'eleadsCRM.apiKey': apiKey,
            'eleadsCRM.lastSync': new Date()
          } 
        },
        { new: true }
      );
      
      if (!dealer) {
        return res.status(404).json({ success: false, error: 'Dealer not found' });
      }
      
      res.json({ success: true, data: dealer, message: 'CRM connected successfully' });
    } catch (error) {
      res.status(400).json({ success: false, error: (error as Error).message });
    }
  },

  // Delete dealer
  async delete(req: Request, res: Response<ApiResponse<null>>) {
    try {
      const dealer = await Dealer.findOneAndDelete({ dealerId: req.params.id });
      if (!dealer) {
        return res.status(404).json({ success: false, error: 'Dealer not found' });
      }
      
      // Also delete all listings for this dealer
      await Listing.deleteMany({ dealerId: req.params.id });
      
      res.json({ success: true, message: 'Dealer deleted' });
    } catch (error) {
      res.status(500).json({ success: false, error: (error as Error).message });
    }
  },

  // Get dealer stats
  async getStats(req: Request, res: Response) {
    try {
      const dealerId = req.params.id;
      
      const stats = await Listing.aggregate([
        { $match: { dealerId } },
        {
          $group: {
            _id: '$status',
            count: { $sum: 1 }
          }
        }
      ]);

      const totalListings = await Listing.countDocuments({ dealerId });
      const publishedVideos = await Listing.countDocuments({ 
        dealerId, 
        status: 'published' 
      });

      res.json({
        success: true,
        data: {
          totalListings,
          publishedVideos,
          statusBreakdown: stats.reduce((acc, s) => {
            acc[s._id] = s.count;
            return acc;
          }, {} as Record<string, number>)
        }
      });
    } catch (error) {
      res.status(500).json({ success: false, error: (error as Error).message });
    }
  }
};

