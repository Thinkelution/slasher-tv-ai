# Slasher TV AI - Automated Motorcycle Video Generator

Automated system for generating 30-second professional motorcycle promo videos from dealer inventory feeds. Built for the **Slasher Sale TV Channel** - a 24/7 livestream of Harley-Davidson deals.

## Overview

The Slasher TV AI system transforms motorcycle inventory data into compelling 30-second video commercials automatically. Each video features:

- Dynamic bike imagery with professional layouts
- AI-generated scripts and voiceovers
- Price reveal animations ("price slash" effect)
- QR codes for instant reservations
- Dealer branding and logos
- Background music and professional audio mixing

## Features

- **Automated CSV Parsing**: Reads dealer inventory feeds
- **Intelligent Image Downloading**: Parallel download of motorcycle photos
- **Background Removal**: AI-powered image processing with rembg
- **AI Script Generation**: OpenAI GPT-4 or Anthropic Claude for compelling ad copy
- **Text-to-Speech**: AI voiceover generation with gTTS
- **Professional Video Composition**: Multiple templates (clean, dark, fire themes)
- **QR Code Generation**: Instant reservation links
- **Cloud Storage**: Cloudflare R2 integration for asset hosting
- **REST API**: FastAPI backend for programmatic access
- **Web Dashboard**: React frontend for easy management
- **Batch Processing**: Handle hundreds of listings efficiently

## Project Structure

```
slasher/
├── src/
│   ├── data/                    # Data processing
│   │   ├── data_models.py       # Pydantic models
│   │   ├── feed_parser.py       # CSV parser
│   │   ├── image_downloader.py  # Image fetcher
│   │   └── asset_manager.py     # Asset organization
│   ├── ai/                      # AI generation
│   │   ├── script_generator.py  # AI script writer
│   │   ├── qr_generator.py      # QR code creator
│   │   ├── image_processor.py   # Background removal
│   │   └── voice_generator.py   # Text-to-Speech
│   ├── api/                     # REST API
│   │   ├── app.py               # FastAPI application
│   │   └── routes.py            # API endpoints
│   ├── utils/                   # Utilities
│   │   └── r2_uploader.py       # Cloudflare R2 integration
│   └── main.py                  # CLI pipeline
├── frontend/                    # React Web Dashboard
│   ├── src/
│   │   ├── App.tsx              # Main application
│   │   └── components/
│   │       ├── GenerateForm.tsx # Generation form
│   │       ├── ListingsTable.tsx# Listings display
│   │       ├── ResultPanel.tsx  # Results viewer
│   │       └── Toast.tsx        # Notifications
│   ├── package.json
│   └── vite.config.ts
├── assets/                      # Downloaded assets
│   ├── branding/
│   ├── backgrounds/
│   ├── music/
│   └── {dealer_id}/{stock_number}/
│       ├── photo_XX.jpg         # Original images
│       ├── processed/           # Processed images
│       │   └── photo_XX_nobg.png
│       ├── script.txt           # Generated script
│       ├── voiceover.mp3        # Generated audio
│       └── qr_code.png          # QR code
├── output/                      # Generated videos
├── config/
│   └── config.yaml              # Configuration
├── run_api.py                   # API server launcher
├── sample-feed.csv              # Sample inventory
├── requirements.txt             # Python dependencies
├── ARCHITECTURE.md              # System architecture docs
├── QUICKSTART.md                # Quick start guide
└── README.md
```

## Installation

### Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend)
- pip
- API keys for OpenAI or Anthropic (for script generation)
- Cloudflare R2 credentials (for cloud storage)

### Setup

1. Clone repository:
```bash
git clone <repository-url>
cd slasher
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. (Optional) For GPU acceleration, install CUDA-enabled PyTorch

## Usage

### Option 1: Web Dashboard (Recommended)

Start the API server and frontend:

```bash
# Terminal 1: Start API server
python run_api.py

# Terminal 2: Start frontend
cd frontend
npm run dev
```

Open http://localhost:5173 in your browser.

### Option 2: Command Line

Process all listings in sample feed:
```bash
python src/main.py
```

Process first 3 listings only:
```bash
python src/main.py --limit 3
```

Process single listing:
```bash
python src/main.py --stock 156359BB
```

### Option 3: REST API

Start the API server:
```bash
python run_api.py
```

API endpoints:
- `GET /api/listings` - Get all listings
- `GET /api/listings/{stock}` - Get single listing
- `POST /api/generate` - Generate assets for a listing
- `GET /api/health` - Health check

### Pipeline Stages

The system runs through these stages:

1. **Parse Feed**: Read CSV inventory data
2. **Download Images**: Fetch all motorcycle photos
3. **Process Images**: Remove backgrounds with AI
4. **Generate Scripts**: Create AI-powered ad copy
5. **Generate Voiceovers**: Text-to-Speech conversion
6. **Generate QR Codes**: Create reservation links
7. **Upload to R2**: Store assets in cloud (optional)

### Example Output

After running the pipeline, you'll have:

```
assets/
  api/                    # API-generated assets
    156359BB/             # Stock Number
      ├── photo_00.jpg    # Original images
      ├── photo_01.jpg
      ├── processed/      # Background-removed images
      │   ├── photo_00_nobg.png
      │   └── photo_01_nobg.png
      ├── script.txt      # Generated script
      ├── voiceover.mp3   # Generated voiceover
      └── qr_code.png     # QR code
```

## Configuration

### Environment Variables (.env)

```bash
# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Cloudflare R2
R2_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-access-key
R2_SECRET_ACCESS_KEY=your-secret-key
R2_BUCKET_NAME=slasher-assets
R2_PUBLIC_URL=https://your-r2-url.r2.dev

# Directories
OUTPUT_DIR=./output
ASSETS_DIR=./assets

# Video Settings
DEFAULT_TEMPLATE=dark
VIDEO_RESOLUTION=1920x1080
VIDEO_FPS=30
```

### Template Configuration (config/config.yaml)

Three visual templates available:

- **clean**: Modern white/gray background
- **dark**: Aggressive dark theme (default)
- **fire**: High-energy fire background

Each template can be customized for:
- Colors and fonts
- Logo placement
- Animation timing
- Audio levels

## Architecture

### Data Flow

```
CSV Feed → Parser → Listings
                      ↓
            Image Downloader → Assets
                      ↓
            Image Processor → Background Removed
                      ↓
            Script Generator → Scripts
                      ↓
            Voice Generator → Voiceovers
                      ↓
            QR Generator → QR Codes
                      ↓
            R2 Uploader → Cloud Storage
                      ↓
         Video Composer → 30s MP4
```

### Video Timeline (30 seconds)

- **0-3s**: SLASHER SALE logo animation
- **3-8s**: Bike reveal with zoom/rotate
- **8-15s**: Feature highlights with callouts
- **15-22s**: Price slash reveal
- **22-27s**: QR code + "SCAN TO RESERVE NOW"
- **27-30s**: Dealer logo + outro

## Development Status

### ✅ Completed

- [x] Project architecture
- [x] CSV feed parser
- [x] Data models (Pydantic)
- [x] Image downloader (parallel)
- [x] Asset manager
- [x] AI script generator (OpenAI/Anthropic)
- [x] QR code generator
- [x] Configuration system
- [x] Main pipeline
- [x] Image processor (background removal with rembg)
- [x] Voice generator (Text-to-Speech with gTTS)
- [x] REST API (FastAPI)
- [x] Web dashboard (React + TypeScript)
- [x] Cloudflare R2 integration

### 🚧 In Progress

- [ ] Video composition engine (MoviePy)
- [ ] Template renderer
- [ ] Animation system
- [ ] Audio mixer

### 📋 Planned

- [ ] Real-time feed ingestion
- [ ] A/B testing for templates
- [ ] Analytics and reporting
- [ ] Cloud deployment (DGX Spark)
- [ ] 24/7 livestream playout

## Sample Data

The project includes `sample-feed.csv` with real Harley-Davidson listings from San Diego Harley-Davidson.

Example listing:
- 2024 Low Rider ST
- 377 miles
- $27,990
- Multiple photos
- Detailed description

## Technology Stack

### Core
- **Python 3.10+**: Main language
- **Pydantic**: Data validation
- **Pandas**: CSV processing

### AI/ML
- **OpenAI GPT-4**: Script generation
- **Anthropic Claude**: Alternative script generation
- **rembg**: Background removal
- **gTTS**: Text-to-Speech

### API & Frontend
- **FastAPI**: REST API framework
- **Uvicorn**: ASGI server
- **React**: Frontend framework
- **TypeScript**: Type-safe JavaScript
- **Vite**: Frontend build tool

### Cloud & Storage
- **Cloudflare R2**: Object storage
- **boto3**: AWS/R2 SDK

### Video (In Progress)
- **MoviePy**: Video composition
- **OpenCV**: Image processing
- **Pillow**: Image manipulation

### Utilities
- **requests**: HTTP downloads
- **tqdm**: Progress bars
- **qrcode**: QR code generation
- **python-dotenv**: Configuration

## Performance

- **CSV Parsing**: ~1000 listings/second
- **Image Download**: 5 concurrent downloads (configurable)
- **Background Removal**: ~2-5 seconds per image
- **Script Generation**: ~5-10 seconds per listing
- **Voice Generation**: ~2-3 seconds per script
- **Video Rendering**: ~30-60 seconds per video (estimated)

## Examples

### Generated Script Example

```
The road is calling. This is your answer.

2024 Low Rider ST. Milwaukee-Eight 117 engine.
125 foot-pounds of pure torque. Touring-ready with
sport-tuned suspension.

Barely broken in at 377 miles. And yours for just
twenty-seven thousand, nine ninety.

Don't wait. Scan to reserve. Available now at
San Diego Harley-Davidson.
```

## Contributing

This is a proprietary project for the Slasher Sale TV Channel.

## License

Proprietary - All rights reserved

## Contact

For questions about this system, contact the development team.

---

**Slasher TV** - 24/7 Harley-Davidson Deals
