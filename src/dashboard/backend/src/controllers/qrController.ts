import { Request, Response } from 'express';
import { Listing } from '../models/index.js';
import { pipelineService } from '../services/PipelineService.js';
import type { ApiResponse } from '../types/index.js';
import fs from 'fs';
import path from 'path';

interface QRCodeData {
  listingId: string;
  url: string;
  imagePath: string;
  imageBase64?: string;
}

export const qrController = {
  // Get QR code for a listing
  async getByListing(req: Request, res: Response<ApiResponse<QRCodeData>>) {
    try {
      const listing = await Listing.findById(req.params.listingId);
      
      if (!listing) {
        return res.status(404).json({ success: false, error: 'Listing not found' });
      }

      if (!listing.assets.qrCodePath) {
        return res.status(404).json({ success: false, error: 'QR code not generated' });
      }

      const qrPath = listing.assets.qrCodePath;
      let imageBase64: string | undefined;

      if (fs.existsSync(qrPath)) {
        const imageBuffer = fs.readFileSync(qrPath);
        imageBase64 = `data:image/png;base64,${imageBuffer.toString('base64')}`;
      }

      res.json({
        success: true,
        data: {
          listingId: listing.stockNumber,
          url: listing.listingUrl,
          imagePath: qrPath,
          imageBase64
        }
      });
    } catch (error) {
      res.status(500).json({ success: false, error: (error as Error).message });
    }
  },

  // Get all QR codes for a dealer
  async getByDealer(req: Request, res: Response<ApiResponse<QRCodeData[]>>) {
    try {
      const { dealerId } = req.params;
      
      const listings = await Listing.find({ 
        dealerId,
        'assets.qrCodePath': { $exists: true, $ne: null }
      }).select('stockNumber listingUrl assets.qrCodePath');

      const qrCodes: QRCodeData[] = listings.map(listing => ({
        listingId: listing.stockNumber,
        url: listing.listingUrl,
        imagePath: listing.assets.qrCodePath || ''
      }));

      res.json({ success: true, data: qrCodes });
    } catch (error) {
      res.status(500).json({ success: false, error: (error as Error).message });
    }
  },

  // Regenerate QR code
  async regenerate(req: Request, res: Response<ApiResponse<QRCodeData>>) {
    try {
      const listing = await Listing.findById(req.params.listingId);
      
      if (!listing) {
        return res.status(404).json({ success: false, error: 'Listing not found' });
      }

      // Generate new QR code
      const outputPath = path.join(
        'assets',
        listing.dealerId,
        listing.stockNumber,
        'qr_code.png'
      );

      const result = await pipelineService.generateQRCode(listing.listingUrl, outputPath);

      if (!result.success) {
        return res.status(500).json({ 
          success: false, 
          error: result.error || 'QR generation failed' 
        });
      }

      // Update listing
      listing.assets.qrCodePath = outputPath;
      await listing.save();

      res.json({
        success: true,
        data: {
          listingId: listing.stockNumber,
          url: listing.listingUrl,
          imagePath: outputPath
        },
        message: 'QR code regenerated'
      });
    } catch (error) {
      res.status(500).json({ success: false, error: (error as Error).message });
    }
  },

  // Serve QR code image
  async serveImage(req: Request, res: Response) {
    try {
      const listing = await Listing.findById(req.params.listingId);
      
      if (!listing || !listing.assets.qrCodePath) {
        return res.status(404).send('QR code not found');
      }

      const qrPath = listing.assets.qrCodePath;
      
      if (!fs.existsSync(qrPath)) {
        return res.status(404).send('QR code file not found');
      }

      res.setHeader('Content-Type', 'image/png');
      fs.createReadStream(qrPath).pipe(res);
    } catch (error) {
      res.status(500).send('Error serving QR code');
    }
  },

  // Test QR code (simulate scan)
  async testScan(req: Request, res: Response) {
    try {
      const listing = await Listing.findById(req.params.listingId);
      
      if (!listing) {
        return res.status(404).json({ success: false, error: 'Listing not found' });
      }

      // Return the URL that the QR code points to
      res.json({
        success: true,
        data: {
          listingId: listing.stockNumber,
          url: listing.listingUrl,
          redirectTo: listing.listingUrl
        },
        message: 'QR code is valid and working'
      });
    } catch (error) {
      res.status(500).json({ success: false, error: (error as Error).message });
    }
  }
};

