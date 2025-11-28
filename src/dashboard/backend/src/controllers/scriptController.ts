import { Request, Response } from 'express';
import { Script, Listing } from '../models/index.js';
import type { ApiResponse, IScript } from '../types/index.js';

export const scriptController = {
  // Get script by listing ID
  async getByListing(req: Request, res: Response<ApiResponse<IScript>>) {
    try {
      const script = await Script.findOne({ listingId: req.params.listingId });
      if (!script) {
        return res.status(404).json({ success: false, error: 'Script not found' });
      }
      res.json({ success: true, data: script });
    } catch (error) {
      res.status(500).json({ success: false, error: (error as Error).message });
    }
  },

  // Get all scripts pending approval
  async getPendingApproval(req: Request, res: Response<ApiResponse<IScript[]>>) {
    try {
      const dealerId = req.query.dealerId as string;
      
      const query: Record<string, unknown> = { status: 'pending_approval' };
      
      // If dealerId provided, filter by dealer's listings
      if (dealerId) {
        const listings = await Listing.find({ dealerId }).select('stockNumber');
        const stockNumbers = listings.map(l => l.stockNumber);
        query.listingId = { $in: stockNumbers };
      }

      const scripts = await Script.find(query).sort({ createdAt: -1 });
      res.json({ success: true, data: scripts });
    } catch (error) {
      res.status(500).json({ success: false, error: (error as Error).message });
    }
  },

  // Update script content
  async update(req: Request, res: Response<ApiResponse<IScript>>) {
    try {
      const { content } = req.body;
      const script = await Script.findById(req.params.id);
      
      if (!script) {
        return res.status(404).json({ success: false, error: 'Script not found' });
      }

      // Save current version to history
      script.versions.push({
        content: script.content,
        createdAt: new Date(),
        createdBy: req.body.editedBy || 'admin'
      });

      // Update content
      script.content = content;
      script.wordCount = content.split(/\s+/).length;
      script.estimatedDuration = Math.ceil(script.wordCount / 2.5); // ~150 words/min
      script.status = 'pending_approval';

      await script.save();

      // Update listing status
      await Listing.findOneAndUpdate(
        { stockNumber: script.listingId },
        { status: 'script_generated' }
      );

      res.json({ success: true, data: script, message: 'Script updated' });
    } catch (error) {
      res.status(400).json({ success: false, error: (error as Error).message });
    }
  },

  // Approve script
  async approve(req: Request, res: Response<ApiResponse<IScript>>) {
    try {
      const script = await Script.findByIdAndUpdate(
        req.params.id,
        {
          status: 'approved',
          approvedBy: req.body.approvedBy || 'admin',
          approvedAt: new Date()
        },
        { new: true }
      );

      if (!script) {
        return res.status(404).json({ success: false, error: 'Script not found' });
      }

      // Update listing status
      await Listing.findOneAndUpdate(
        { stockNumber: script.listingId },
        { status: 'script_approved' }
      );

      res.json({ success: true, data: script, message: 'Script approved' });
    } catch (error) {
      res.status(400).json({ success: false, error: (error as Error).message });
    }
  },

  // Reject script
  async reject(req: Request, res: Response<ApiResponse<IScript>>) {
    try {
      const { reason } = req.body;
      
      const script = await Script.findByIdAndUpdate(
        req.params.id,
        {
          status: 'rejected',
          rejectionReason: reason
        },
        { new: true }
      );

      if (!script) {
        return res.status(404).json({ success: false, error: 'Script not found' });
      }

      res.json({ success: true, data: script, message: 'Script rejected' });
    } catch (error) {
      res.status(400).json({ success: false, error: (error as Error).message });
    }
  },

  // Get script versions/history
  async getVersions(req: Request, res: Response) {
    try {
      const script = await Script.findById(req.params.id).select('versions content');
      if (!script) {
        return res.status(404).json({ success: false, error: 'Script not found' });
      }
      
      res.json({ 
        success: true, 
        data: {
          current: script.content,
          versions: script.versions
        }
      });
    } catch (error) {
      res.status(500).json({ success: false, error: (error as Error).message });
    }
  },

  // Revert to previous version
  async revertVersion(req: Request, res: Response<ApiResponse<IScript>>) {
    try {
      const { versionIndex } = req.body;
      const script = await Script.findById(req.params.id);
      
      if (!script) {
        return res.status(404).json({ success: false, error: 'Script not found' });
      }

      if (versionIndex < 0 || versionIndex >= script.versions.length) {
        return res.status(400).json({ success: false, error: 'Invalid version index' });
      }

      // Save current as new version
      script.versions.push({
        content: script.content,
        createdAt: new Date(),
        createdBy: 'admin (revert)'
      });

      // Revert to selected version
      script.content = script.versions[versionIndex].content;
      script.wordCount = script.content.split(/\s+/).length;
      script.estimatedDuration = Math.ceil(script.wordCount / 2.5);
      script.status = 'pending_approval';

      await script.save();

      res.json({ success: true, data: script, message: 'Reverted to previous version' });
    } catch (error) {
      res.status(400).json({ success: false, error: (error as Error).message });
    }
  }
};

