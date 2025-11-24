# Quick Start Guide - Slasher TV AI

## Get Started in 5 Minutes

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your OpenAI API key:
OPENAI_API_KEY=sk-your-key-here
```

### 3. Test with Sample Data

Process first 3 listings from sample feed:

```bash
python src/main.py --limit 3
```

This will:
- Parse `sample-feed.csv`
- Download motorcycle images
- Generate AI scripts
- Create QR codes

### 4. Check Results

```bash
# View generated assets
ls assets/4802/

# Example output:
# 156359BB/     - 2002 Sportster 883 Custom
# 705108BB/     - 2007 Electra Glide
# 056106BB/     - 2024 Low Rider ST
```

Each listing folder contains:
- `metadata.json` - Listing details
- `photo_*.jpg` - Downloaded images
- `script.txt` - AI-generated script
- `qr_code.png` - QR code for listing

### 5. Read a Generated Script

```bash
cat assets/4802/156359BB/script.txt
```

## Next Steps

### Process All Listings

```bash
python src/main.py
```

### Process Single Listing

```bash
python src/main.py --stock 156359BB
```

### Custom Configuration

Edit `config/config.yaml` to customize:
- Video templates (clean, dark, fire)
- Animation timing
- Font styles
- Colors

## What Works Now

- ✅ CSV feed parsing
- ✅ Image downloading (parallel)
- ✅ AI script generation (OpenAI/Anthropic)
- ✅ QR code generation
- ✅ Asset management

## Coming Next

- 🚧 Video composition with MoviePy
- 🚧 Text-to-speech voiceovers
- 🚧 Background removal for images
- 🚧 Price slash animations
- 🚧 Full 30-second video rendering

## Troubleshooting

### Missing API Key
```
Error: OPENAI_API_KEY not found
Solution: Add your key to .env file
```

### Import Errors
```
Error: No module named 'openai'
Solution: pip install -r requirements.txt
```

### CSV Not Found
```
Error: CSV feed not found
Solution: Make sure sample-feed.csv is in root directory
```

## Example: Generated Script

```
Born to dominate. The 2002 Sportster 883 Custom.

Fully transformed into a café racer masterpiece.
Progressive suspension. Custom controls. Baja Design lighting.

Every inch crafted for the discerning rider who values
performance and individuality.

Just sixty-nine ninety-nine. Don't wait. Scan to reserve.
Available now at San Diego Harley-Davidson.
```

## Performance

- **Parsing**: Instant (1000+ listings/sec)
- **Image Download**: ~2-5 seconds per listing
- **Script Generation**: ~3-5 seconds per listing
- **Total**: ~10-15 seconds per listing

## Need Help?

Check the full [README.md](README.md) for detailed documentation.
