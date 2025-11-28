import { Router } from 'express';
import { dealerController } from '../controllers/dealerController.js';
import { listingController } from '../controllers/listingController.js';
import { scriptController } from '../controllers/scriptController.js';
import { videoController } from '../controllers/videoController.js';
import { qrController } from '../controllers/qrController.js';

const router = Router();

// ==================== DEALER ROUTES ====================
router.get('/dealers', dealerController.getAll);
router.get('/dealers/:id', dealerController.getById);
router.post('/dealers', dealerController.create);
router.put('/dealers/:id', dealerController.update);
router.put('/dealers/:id/settings', dealerController.updateSettings);
router.post('/dealers/:id/crm/connect', dealerController.connectEleadsCRM);
router.delete('/dealers/:id', dealerController.delete);
router.get('/dealers/:id/stats', dealerController.getStats);

// ==================== LISTING ROUTES ====================
router.get('/dealers/:dealerId/listings', listingController.getByDealer);
router.get('/listings/:id', listingController.getById);
router.put('/listings/:id/photos', listingController.updatePhotos);
router.post('/listings/:id/regenerate-video', listingController.regenerateVideo);
router.get('/listings/:id/assets', listingController.getAssets);
router.delete('/listings/:id', listingController.delete);

// ==================== SCRIPT ROUTES ====================
router.get('/scripts/pending', scriptController.getPendingApproval);
router.get('/scripts/listing/:listingId', scriptController.getByListing);
router.put('/scripts/:id', scriptController.update);
router.post('/scripts/:id/approve', scriptController.approve);
router.post('/scripts/:id/reject', scriptController.reject);
router.get('/scripts/:id/versions', scriptController.getVersions);
router.post('/scripts/:id/revert', scriptController.revertVersion);

// ==================== VIDEO ROUTES ====================
router.get('/dealers/:dealerId/videos', videoController.getByDealer);
router.get('/videos/pending', videoController.getPendingApproval);
router.get('/videos/:id', videoController.getById);
router.get('/videos/:id/stream', videoController.stream);
router.post('/videos/:id/approve', videoController.approve);
router.post('/videos/:id/reject', videoController.reject);
router.post('/videos/:id/publish', videoController.publish);
router.post('/videos/:id/regenerate', videoController.regenerate);
router.delete('/videos/:id', videoController.delete);

// ==================== QR CODE ROUTES ====================
router.get('/qr/listing/:listingId', qrController.getByListing);
router.get('/qr/dealer/:dealerId', qrController.getByDealer);
router.post('/qr/:listingId/regenerate', qrController.regenerate);
router.get('/qr/:listingId/image', qrController.serveImage);
router.get('/qr/:listingId/test', qrController.testScan);

export default router;

