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
- **AI Script Generation**: OpenAI GPT-4 or Anthropic Claude for compelling ad copy
- **Professional Video Composition**: Multiple templates (clean, dark, fire themes)
- **QR Code Generation**: Instant reservation links
- **Asset Management**: Organized file structure for all media
- **Batch Processing**: Handle hundreds of listings efficiently

## Project Structure

```
slasher-tv-ai/
├── src/
│   ├── data/                    # Data processing
│   │   ├── data_models.py       # Pydantic models
│   │   ├── feed_parser.py       # CSV parser
│   │   ├── image_downloader.py  # Image fetcher
│   │   └── asset_manager.py     # Asset organization
│   ├── ai/                      # AI generation
│   │   ├── script_generator.py  # AI script writer
│   │   └── qr_generator.py      # QR code creator
│   ├── video/                   # Video composition (coming soon)
│   │   ├── video_composer.py
│   │   └── templates/
│   └── main.py                  # Main pipeline
├── assets/                      # Downloaded assets
│   ├── branding/
│   ├── backgrounds/
│   ├── music/
│   └── {dealer_id}/{stock_number}/
├── output/                      # Generated videos
├── config/
│   └── config.yaml              # Configuration
├── sample-feed.csv              # Sample inventory
├── requirements.txt             # Python dependencies
└── README.md
```

## Installation

### Prerequisites

- Python 3.10+
- pip
- API keys for OpenAI or Anthropic (for script generation)

### Setup

1. Clone repository:
```bash
git clone <repository-url>
cd slasher-tv-ai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. (Optional) For GPU acceleration, install CUDA-enabled PyTorch

## Usage

### Quick Start

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

### Pipeline Stages

The system runs through 5 stages:

1. **Parse Feed**: Read CSV inventory data
2. **Download Images**: Fetch all motorcycle photos
3. **Save Metadata**: Store listing information
4. **Generate Scripts**: Create AI-powered ad copy
5. **Generate QR Codes**: Create reservation links

### Example Output

After running the pipeline, you'll have:

```
assets/
  4802/                    # Dealer ID
    156359BB/              # Stock Number
      ├── metadata.json    # Listing data
      ├── photo_00.jpg     # Original images
      ├── photo_01.jpg
      ├── script.txt       # Generated script
      └── qr_code.png      # QR code
```

## Configuration

### Environment Variables (.env)

```bash
# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

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
            Script Generator → Scripts
                      ↓
            QR Generator → QR Codes
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

### 🚧 In Progress

- [ ] Image processor (background removal, enhancement)
- [ ] Voice generator (Text-to-Speech)
- [ ] Video composition engine (MoviePy)
- [ ] Template renderer
- [ ] Animation system
- [ ] Audio mixer

### 📋 Planned

- [ ] Web dashboard for monitoring
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
- **rembg**: Background removal (planned)

### Video (Planned)
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
- **Script Generation**: ~5-10 seconds per listing
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
