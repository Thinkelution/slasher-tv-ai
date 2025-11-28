# 🏍️ Slasher TV AI - Motorcycle Video Generator

Automated system for generating 30-second promotional videos from dealer motorcycle inventory feeds.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Overview

Slasher TV AI transforms dealer inventory CSV feeds into professional 30-second video commercials. The system automatically:

1. **Parses** inventory data from CSV feeds
2. **Downloads** motorcycle images from URLs
3. **Processes** images with AI background removal (99% clean extraction)
4. **Generates** ad scripts using AI
5. **Creates** voiceovers with text-to-speech
6. **Composes** final videos with animations and branding

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run pipeline (1 listing, assets only)
python run.py --limit 1 --skip-video

# Run full pipeline with video
python run.py --limit 1
```

## Project Structure

```
slasher-tv-ai/
├── run.py                    # Quick run script
├── sample-feed.csv           # Input: Dealer inventory
├── requirements.txt          # Dependencies
│
├── src/
│   ├── main.py              # Complete pipeline orchestrator
│   │
│   ├── data/                # Phase 1: Data Ingestion
│   │   ├── feed_parser.py       # Parse CSV → MotorcycleListing
│   │   ├── data_models.py       # Pydantic data models
│   │   ├── image_downloader.py  # Download photos from URLs
│   │   └── asset_manager.py     # Organize assets by dealer/SKU
│   │
│   ├── ai/                  # Phase 2: AI Generation
│   │   ├── image_processor_v2.py  # AI background removal
│   │   ├── script_generator.py    # AI ad copy generation
│   │   ├── voice_generator.py     # Text-to-speech synthesis
│   │   └── qr_generator.py        # QR code generation
│   │
│   └── video/               # Phase 3: Video Production
│       ├── video_composer.py     # Main video engine
│       ├── audio_mixer.py        # Mix voiceover + music
│       └── templates/            # Video templates
│           ├── dark_template.py
│           └── simple_dark_template.py
│
├── assets/                  # Generated assets
│   └── {dealer_id}/{stock_number}/
│       ├── photo_*.jpg          # Original images
│       ├── processed/*.png      # Background removed
│       ├── metadata.json        # Listing data
│       ├── script.txt           # Ad script
│       ├── voiceover.mp3        # Audio
│       └── qr_code.png          # QR code
│
├── output/                  # Final videos
│   └── {stock_number}_dark.mp4
│
└── config/
    └── config.yaml          # Configuration
```

## Workflow

### Phase 1: Data Ingestion
```
CSV Feed → Parser → Download Images → Save Metadata
```

| Component | Input | Output |
|-----------|-------|--------|
| `feed_parser.py` | `sample-feed.csv` | `MotorcycleListing` objects |
| `image_downloader.py` | Photo URLs | `photo_*.jpg` files |
| `asset_manager.py` | Listings | `metadata.json` |

### Phase 2: AI Generation
```
Images → Background Removal → Script → Voiceover → QR Code
```

| Component | Input | Output |
|-----------|-------|--------|
| `image_processor_v2.py` | JPG photos | PNG (transparent background) |
| `script_generator.py` | Bike specs | `script.txt` (30-second ad copy) |
| `voice_generator.py` | Script text | `voiceover.mp3` |
| `qr_generator.py` | Listing URL | `qr_code.png` |

### Phase 3: Video Production
```
Assets + Template → Video Composer → 30-second MP4
```

| Component | Input | Output |
|-----------|-------|--------|
| `video_composer.py` | All assets | `{stock_number}.mp4` |

## Usage

### Basic Usage

```bash
# Process all listings
python run.py

# Process first N listings
python run.py --limit 3

# Generate assets only (no video)
python run.py --limit 1 --skip-video

# Use specific template
python run.py --limit 1 --template dark
```

### Advanced Usage

```bash
# Using main.py directly
python -m src.main --csv sample-feed.csv --limit 1

# Custom directories
python -m src.main --assets-dir ./my_assets --output-dir ./my_output

# Full options
python -m src.main --csv sample-feed.csv --limit 5 --template dark --skip-video
```

### Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--csv` | `sample-feed.csv` | Path to inventory CSV feed |
| `--limit` | All | Number of listings to process |
| `--assets-dir` | `./assets` | Directory for generated assets |
| `--output-dir` | `./output` | Directory for final videos |
| `--template` | `dark` | Video template (dark, clean, fire) |
| `--skip-video` | False | Skip video generation (assets only) |

## Configuration

### Environment Variables (.env)

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
ELEVENLABS_API_KEY=...
REMOVEBG_API_KEY=...         # Remove.bg API for background removal
```

### Video Output Specs

- **Resolution:** 1920x1080 (Full HD)
- **Frame Rate:** 30 fps
- **Duration:** 30 seconds
- **Codec:** H.264
- **Audio:** AAC 192kbps

## Image Processing

The `image_processor_v2.py` uses **Remove.bg API** for professional background removal with rembg fallback:

### Features
- **Remove.bg API** - Professional cloud-based background removal (50 free calls/month)
- **rembg fallback** - Local processing if API unavailable
- **Halo removal** - Clean edges without artifacts
- **Auto-cropping** - Tight crop to motorcycle bounds
- **Quality analysis** - Reports extraction quality

### Usage

```python
from src.ai import ImageProcessor

# With Remove.bg API (set REMOVEBG_API_KEY in .env)
processor = ImageProcessor()

# Or force local rembg processing
processor = ImageProcessor(use_api=False)

processor.process_batch(
    input_dir="assets/4802/156359BB",
    output_dir="assets/4802/156359BB/processed",
    pattern="photo_*.jpg"
)
```

### Get Remove.bg API Key
1. Sign up at [remove.bg](https://www.remove.bg/)
2. Go to API section in your dashboard
3. Copy your API key
4. Add to `.env`: `REMOVEBG_API_KEY=your_key_here`

## Video Templates

### Dark Template
- Dark dramatic background
- Red accent colors
- Impact font styling
- Aggressive animations

### Clean Template (Coming Soon)
- White/gray background
- Professional styling
- Clean typography

### Fire Template (Coming Soon)
- Animated fire background
- Intense visual effects

## API Reference

### SlasherTVPipeline

```python
from src.main import SlasherTVPipeline

pipeline = SlasherTVPipeline(
    csv_path="sample-feed.csv",
    assets_dir="./assets",
    output_dir="./output",
    template="dark"
)

# Run full pipeline
pipeline.run(limit=1, skip_video=False)

# Run individual phases
listings = pipeline.phase1_parse_feed(limit=1)
pipeline.phase1_download_images(listings)
pipeline.phase2_process_images(listings)
pipeline.phase2_generate_scripts(listings)
pipeline.phase2_generate_voiceovers(listings)
pipeline.phase3_create_videos(listings)
```

### ImageProcessor

```python
from src.ai import ImageProcessor

processor = ImageProcessor(model="isnet-general-use")

# Process single image
success, quality = processor.process(
    input_path="photo.jpg",
    output_path="photo_clean.png"
)

# Process batch
stats = processor.process_batch(
    input_dir="./images",
    output_dir="./processed",
    pattern="*.jpg"
)
```

### VoiceGenerator

```python
from src.ai import VoiceGenerator

voice = VoiceGenerator(provider="gtts", default_style="aggressive")

# Generate from text
voice.generate_voiceover(
    text="Own the road. 2023 Road Glide ST.",
    output_path="voiceover.mp3",
    style="aggressive"
)

# Generate from script file
voice.generate_from_script_file(
    script_path="script.txt",
    output_path="voiceover.mp3"
)
```

## Requirements

```
# Core
python>=3.10
pandas>=2.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0

# Image Processing
Pillow>=10.0.0
opencv-python>=4.8.0
numpy>=1.24.0
rembg>=2.0.50

# AI/ML
openai>=1.0.0
anthropic>=0.18.0
gtts>=2.3.0

# Video
moviepy>=1.0.3

# Utilities
requests>=2.31.0
tqdm>=4.65.0
qrcode>=7.4.0
```

## Installation

```bash
# Clone repository
git clone https://github.com/your-repo/slasher-tv-ai.git
cd slasher-tv-ai

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

## Troubleshooting

### Image Processing Issues

**Problem:** Background not fully removed
```bash
# Try processing with different settings
python -c "from src.ai import ImageProcessor; p = ImageProcessor(); p.process('input.jpg', 'output.png')"
```

**Problem:** Missing handlebars/parts
- The v2.3 processor includes handlebar recovery
- Check the "Recovered X handlebar pixels" log message

### Video Generation Issues

**Problem:** MoviePy not found
```bash
pip install moviepy
```

**Problem:** Audio codec issues
```bash
# Install ffmpeg
# Windows: choco install ffmpeg
# Mac: brew install ffmpeg
# Linux: apt install ffmpeg
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and feature requests, please open a GitHub issue.

---

**Slasher TV AI** - Automated Motorcycle Video Generation
