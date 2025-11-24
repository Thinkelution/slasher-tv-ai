# Slasher TV AI - Video Generation Architecture

## Overview
Automated system for generating 30-second motorcycle promo videos from dealer inventory feeds.

## System Architecture

### 1. Data Pipeline Layer
```
CSV Feed → Parser → Normalized JSON → Asset Manager
```

**Components:**
- `feed_parser.py`: Parse CSV inventory feeds
- `image_downloader.py`: Download bike images from URLs
- `asset_manager.py`: Organize media by dealer/SKU structure
- `data_models.py`: Pydantic models for data validation

**Output:** `/assets/{dealer_id}/{stock_number}/`
- Original bike images
- Processed images (background removed)
- Metadata JSON

### 2. AI Generation Layer
```
Inventory Data → Script Generator → TTS Engine → Audio Files
                ↓
         Image Processor → Enhanced Images
```

**Components:**
- `script_generator.py`: AI-powered ad copy creation (OpenAI/Anthropic)
- `voice_generator.py`: Text-to-speech synthesis (ElevenLabs/gTTS)
- `image_processor.py`: Background removal, upscaling, enhancement
- `qr_generator.py`: Generate QR codes for listings

**Features:**
- 30-second script templates
- Dynamic copy based on bike specs
- Multiple voice styles (aggressive, smooth, professional)
- Background removal for clean compositing

### 3. Video Composition Engine
```
Assets + Script + Audio → Template Renderer → 30s Video
```

**Components:**
- `video_composer.py`: Main video generation engine
- `templates/`: Visual template configurations
  - `clean_template.py`: White/gray background style
  - `dark_template.py`: Dark dramatic style
  - `fire_template.py`: Aggressive fire background
- `animations.py`: Price slash effects, transitions
- `audio_mixer.py`: Mix voiceover + background music

**Video Structure (30 seconds):**
```
0-3s:   Brand intro (SLASHER SALE logo animation)
3-8s:   Bike reveal (hero image, rotate/zoom)
8-15s:  Feature highlights (spec callouts, animations)
15-22s: Price slash reveal (dramatic price drop)
22-27s: CTA with QR code (SCAN TO RESERVE NOW)
27-30s: Dealer logo + outro
```

### 4. Rendering Pipeline
```
Video Composer → MoviePy Renderer → MP4 Export → Playout System
```

**Output Specs:**
- Resolution: 1920x1080 (Full HD)
- Frame Rate: 30fps
- Codec: H.264
- Duration: 30 seconds exactly
- Audio: AAC 192kbps

## Technology Stack

### Core Libraries
- **Python 3.10+**: Main language
- **MoviePy**: Video editing and composition
- **Pillow (PIL)**: Image manipulation
- **OpenCV**: Advanced image processing
- **NumPy**: Numerical operations

### AI/ML Services
- **OpenAI GPT-4**: Script generation
- **Anthropic Claude**: Alternative script generation
- **rembg**: Background removal (U2-Net model)
- **ElevenLabs**: Premium voice synthesis
- **gTTS**: Google Text-to-Speech (fallback)

### Utilities
- **qrcode**: QR code generation
- **pandas**: CSV data handling
- **requests**: Image downloading
- **python-dotenv**: Configuration management

## Workflow

### Phase 1: Data Ingestion
1. Load `sample-feed.csv`
2. Parse each motorcycle listing
3. Download all images from "Photo Url List"
4. Store in organized directory structure
5. Generate metadata JSON

### Phase 2: Content Generation
1. For each listing:
   - Generate 30-second ad script
   - Create voiceover audio
   - Process images (remove backgrounds, enhance)
   - Generate QR code with listing URL

### Phase 3: Video Production
1. Select visual template (clean/dark/fire)
2. Compose video layers:
   - Background layer
   - Bike image layer (with animations)
   - Text overlays (year, make, model, price)
   - Graphics (SLASHER SALE branding)
   - QR code
3. Add audio track (voiceover + music)
4. Render 30-second MP4

### Phase 4: Export & Playout
1. Save video to `/output/{stock_number}.mp4`
2. Generate playlist manifest
3. Queue for 24/7 livestream playout

## Directory Structure
```
slasher-tv-ai/
├── src/
│   ├── data/
│   │   ├── feed_parser.py
│   │   ├── image_downloader.py
│   │   ├── asset_manager.py
│   │   └── data_models.py
│   ├── ai/
│   │   ├── script_generator.py
│   │   ├── voice_generator.py
│   │   ├── image_processor.py
│   │   └── qr_generator.py
│   ├── video/
│   │   ├── video_composer.py
│   │   ├── templates/
│   │   │   ├── base_template.py
│   │   │   ├── clean_template.py
│   │   │   ├── dark_template.py
│   │   │   └── fire_template.py
│   │   ├── animations.py
│   │   └── audio_mixer.py
│   └── main.py
├── assets/
│   ├── branding/
│   │   └── slasher_sale_logo.png
│   ├── backgrounds/
│   ├── music/
│   └── {dealer_id}/{stock_number}/
├── output/
├── config/
│   ├── config.yaml
│   └── templates.yaml
├── sample-feed.csv
├── requirements.txt
└── README.md
```

## Configuration

### Environment Variables (.env)
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
ELEVENLABS_API_KEY=...
DEFAULT_TEMPLATE=dark
OUTPUT_DIR=./output
ASSETS_DIR=./assets
```

### Video Templates (config/templates.yaml)
```yaml
templates:
  clean:
    background: "#E5E5E5"
    accent_color: "#FF0000"
    font: "Arial Bold"
  dark:
    background: "#1a1a1a"
    accent_color: "#FF0000"
    font: "Impact"
  fire:
    background_video: "assets/backgrounds/fire.mp4"
    accent_color: "#FF0000"
    font: "Impact"
```

## Next Steps
1. Set up project structure
2. Implement CSV parser
3. Build image downloader
4. Create AI script generator
5. Develop video composition engine
6. Test with sample data
7. Deploy to GPU server (NVIDIA DGX Spark)
