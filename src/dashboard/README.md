# Slasher TV AI - Admin Dashboard

A modern MERN stack admin dashboard for managing the Slasher TV AI video production pipeline.

## Features

### Admin Requirements Covered

1. ✅ **Easy to use dashboard** - Manage each dealer's CSV in its own project
2. ✅ **Set/confirm video duration** - Configure 15s, 30s, 45s, or 60s per session
3. ✅ **Approve/edit scripts** - Read, edit, and approve audio scripts
4. ✅ **Approve videos** - Preview and approve videos before publishing
5. ✅ **Replace photos/videos** - Update media per bike as needed
6. ✅ **Add photos/videos** - Add additional media per bike
7. ✅ **Regenerate video on demand** - Re-create videos with one click
8. ✅ **Monitor FAST channel** - View playlist from Live Playout
9. ✅ **View and test QR codes** - Preview and verify QR codes work
10. ✅ **Connect Eleads CRM** - Link dealer's CRM accounts

## Tech Stack

- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Backend**: Express.js + TypeScript + MongoDB
- **State Management**: Zustand + React Query
- **UI Components**: Custom components with Lucide icons

## Project Structure

```
dashboard/
├── backend/
│   ├── src/
│   │   ├── controllers/    # Route handlers
│   │   ├── models/         # MongoDB models
│   │   ├── routes/         # API routes
│   │   ├── services/       # Business logic
│   │   ├── types/          # TypeScript types
│   │   └── index.ts        # Entry point
│   ├── package.json
│   └── tsconfig.json
│
└── frontend/
    ├── src/
    │   ├── components/     # Reusable components
    │   ├── pages/          # Page components
    │   ├── services/       # API services
    │   ├── store/          # Zustand store
    │   ├── types/          # TypeScript types
    │   ├── App.tsx
    │   └── main.tsx
    ├── package.json
    ├── vite.config.ts
    └── tailwind.config.js
```

## Quick Start

### Prerequisites

- Node.js 18+
- MongoDB (local or Atlas)
- Python pipeline (parent directory)

### 1. Install Dependencies

```bash
# Backend
cd dashboard/backend
npm install

# Frontend
cd ../frontend
npm install
```

### 2. Configure Environment

Create `.env` file in `dashboard/backend/`:

```env
MONGODB_URI=mongodb://localhost:27017/slasher-tv
PORT=5000
NODE_ENV=development
PIPELINE_PATH=../../
FRONTEND_URL=http://localhost:5173
```

### 3. Start Development Servers

```bash
# Terminal 1 - Backend
cd dashboard/backend
npm run dev

# Terminal 2 - Frontend
cd dashboard/frontend
npm run dev
```

### 4. Access Dashboard

Open http://localhost:5173 in your browser.

## API Endpoints

### Dealers
- `GET /api/dealers` - List all dealers
- `POST /api/dealers` - Create dealer
- `PUT /api/dealers/:id` - Update dealer
- `PUT /api/dealers/:id/settings` - Update settings
- `DELETE /api/dealers/:id` - Delete dealer

### Scripts
- `GET /api/scripts/pending` - Get pending scripts
- `PUT /api/scripts/:id` - Update script
- `POST /api/scripts/:id/approve` - Approve script
- `POST /api/scripts/:id/reject` - Reject script

### Videos
- `GET /api/videos/pending` - Get pending videos
- `GET /api/videos/:id/stream` - Stream video
- `POST /api/videos/:id/approve` - Approve video
- `POST /api/videos/:id/publish` - Publish to FAST

### QR Codes
- `GET /api/qr/listing/:id` - Get QR code
- `GET /api/qr/:id/image` - Serve QR image
- `GET /api/qr/:id/test` - Test QR code

## Screenshots

### Dashboard
- Overview stats
- Recent activity
- Pipeline status
- Quick actions

### Dealers Management
- Add/edit dealers
- Configure video duration
- Connect CRM
- View stats

### Script Approval
- Read scripts
- Edit content
- View history
- Approve/reject

### Video Review
- Preview videos
- Approve/reject
- Publish to FAST
- Regenerate

### QR Code Viewer
- View all QR codes
- Test functionality
- Download images

## Development

### Backend Commands

```bash
npm run dev      # Start with hot reload
npm run build    # Build for production
npm start        # Run production build
```

### Frontend Commands

```bash
npm run dev      # Start Vite dev server
npm run build    # Build for production
npm run preview  # Preview production build
```

## Production Deployment

### Build

```bash
# Backend
cd dashboard/backend
npm run build

# Frontend
cd dashboard/frontend
npm run build
```

### Environment Variables

Set these in production:

```env
MONGODB_URI=mongodb+srv://...
NODE_ENV=production
PORT=5000
```

## Integration with Python Pipeline

The dashboard communicates with the Python pipeline through the `PipelineService`:

```typescript
// Run full pipeline
await pipelineService.runPipeline(dealerId, { limit: 10 });

// Process images
await pipelineService.processImages(inputDir, outputDir);

// Generate script
await pipelineService.generateScript(listingData);

// Generate video
await pipelineService.generateVideo(listingId, dealerId);
```

## License

MIT

