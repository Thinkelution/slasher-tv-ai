"""
API Routes for Slasher TV AI Video Generation
"""

import sys
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data import FeedParser, ImageDownloader, AssetManager
from src.ai import ScriptGenerator, VoiceGenerator, QRGenerator, ImageProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


# Request model matching frontend form
class GenerateRequest(BaseModel):
    """Request model matching frontend GenerateForm"""
    stock_number: str
    vin: Optional[str] = None
    year: str
    make: str = "Harley-Davidson"
    model: str
    price: str
    condition: str = "Used"
    color: Optional[str] = None
    odometer: Optional[str] = None
    engine_displacement: Optional[str] = None
    voice_style: str = "aggressive"
    listing_url: Optional[str] = None
    description: Optional[str] = None
    photo_urls: Optional[str] = None  # Comma-separated URLs
    background_music: Optional[str] = "none"
    music_volume: int = 30
    
    # Optional settings
    max_images: int = Field(default=2, description="Max images to process")
    process_images: bool = Field(default=True, description="Enable background removal")


class GenerateResponse(BaseModel):
    """Response model for video generation"""
    success: bool
    stock_number: str
    listing_dir: str
    assets: dict
    message: str


@router.post("/generate", response_model=GenerateResponse)
async def generate_video(request: GenerateRequest):
    """
    Generate video assets for a motorcycle listing
    
    Combines Phase 1 (data/images) + Phase 2 (AI generation):
    1. Download images from URLs
    2. Process images (background removal)
    3. Generate AI script
    4. Generate voiceover
    5. Generate QR code
    """
    try:
        logger.info(f"Starting generation for stock #{request.stock_number}")
        
        # Initialize components
        asset_manager = AssetManager(assets_dir="./assets")
        
        # Create a mock listing object for asset management
        dealer_id = "api"  # Use 'api' as dealer ID for API-generated content
        listing_dir = Path(f"./assets/{dealer_id}/{request.stock_number}")
        listing_dir.mkdir(parents=True, exist_ok=True)
        
        results = {
            "images_downloaded": 0,
            "images_processed": 0,
            "script_generated": False,
            "voiceover_generated": False,
            "qr_generated": False
        }
        
        # Step 1: Download images from URLs
        if request.photo_urls:
            photo_list = [url.strip() for url in request.photo_urls.split(",") if url.strip()]
            if photo_list:
                logger.info(f"Downloading {len(photo_list)} images...")
                downloader = ImageDownloader(assets_dir="./assets")
                
                for idx, url in enumerate(photo_list):
                    try:
                        output_path = listing_dir / f"photo_{idx:02d}.jpg"
                        downloader.download_single_image(url, output_path)
                        results["images_downloaded"] += 1
                    except Exception as e:
                        logger.warning(f"Failed to download image {idx}: {e}")
        
        # Step 2: Process images (background removal)
        if request.process_images and results["images_downloaded"] > 0:
            logger.info("Processing images (background removal)...")
            try:
                img_processor = ImageProcessor()
                process_results = img_processor.process_listing_images(
                    listing_dir=listing_dir,
                    process_all=False,
                    max_images=request.max_images
                )
                results["images_processed"] = sum(1 for r in process_results if r.success)
            except Exception as e:
                logger.warning(f"Image processing failed: {e}")
        
        # Step 3: Generate AI Script
        logger.info("Generating AI script...")
        try:
            script_gen = ScriptGenerator(provider="openai")
            script = script_gen.generate_script(
                year=int(request.year),
                make=request.make,
                model=request.model,
                price=float(request.price.replace(",", "").replace("$", "")),
                description=request.description,
                color=request.color,
                mileage=int(request.odometer) if request.odometer else None,
                engine=request.engine_displacement,
                is_custom=False,
                style=request.voice_style
            )
            
            # Save script
            script_path = listing_dir / "script.txt"
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script)
            results["script_generated"] = True
            results["script"] = script
            
        except Exception as e:
            logger.error(f"Script generation failed: {e}")
            results["script_error"] = str(e)
        
        # Step 4: Generate Voiceover
        if results.get("script_generated"):
            logger.info("Generating voiceover...")
            try:
                voice_gen = VoiceGenerator(voice_name="dan")
                audio_path = listing_dir / "voiceover.mp3"
                
                voice_gen.generate_tv_commercial(
                    script=script,
                    output_path=audio_path,
                    style=request.voice_style
                )
                results["voiceover_generated"] = True
                
            except Exception as e:
                logger.error(f"Voiceover generation failed: {e}")
                results["voiceover_error"] = str(e)
        
        # Step 5: Generate QR Code
        if request.listing_url:
            logger.info("Generating QR code...")
            try:
                qr_gen = QRGenerator()
                qr_path = listing_dir / "qr_code.png"
                qr_gen.generate_qr_code(
                    url=request.listing_url,
                    output_path=qr_path,
                    size=(400, 400)
                )
                results["qr_generated"] = True
                
            except Exception as e:
                logger.error(f"QR generation failed: {e}")
        
        logger.info(f"Generation complete for stock #{request.stock_number}")
        
        return GenerateResponse(
            success=True,
            stock_number=request.stock_number,
            listing_dir=str(listing_dir),
            assets=results,
            message="Video assets generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/listings")
async def get_listings(limit: int = 10):
    """Get listings from sample CSV feed"""
    try:
        parser = FeedParser("sample-feed.csv")
        listings = parser.parse()[:limit]
        
        return {
            "count": len(listings),
            "listings": [
                {
                    "stock_number": l.stock_number,
                    "year": l.year,
                    "make": l.make,
                    "model": l.model,
                    "price": l.price,
                    "condition": l.condition,
                    "color": l.color,
                    "odometer": l.odometer
                }
                for l in listings
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assets/{dealer_id}/{stock_number}")
async def get_assets(dealer_id: str, stock_number: str):
    """Get generated assets for a listing"""
    listing_dir = Path(f"./assets/{dealer_id}/{stock_number}")
    
    if not listing_dir.exists():
        raise HTTPException(status_code=404, detail="Assets not found")
    
    files = list(listing_dir.glob("*"))
    
    return {
        "dealer_id": dealer_id,
        "stock_number": stock_number,
        "directory": str(listing_dir),
        "files": [f.name for f in files]
    }

