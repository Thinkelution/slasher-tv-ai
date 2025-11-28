"""
Slasher TV AI - Complete Video Generation Pipeline
===================================================
Automated system for generating 30-second motorcycle promo videos

Workflow:
1. Parse CSV feed → MotorcycleListing objects
2. Download images from URLs
3. Process images (AI background removal)
4. Generate ad scripts
5. Create voiceovers
6. Generate QR codes
7. Compose final video
"""

import os
import sys
from pathlib import Path
import logging
import argparse
from typing import List, Optional
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data import FeedParser, ImageDownloader, AssetManager, MotorcycleListing
from src.ai import ScriptGenerator, QRGenerator, VoiceGenerator, ImageProcessor
from src.video import VideoComposer

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SlasherTVPipeline:
    """
    Complete pipeline for motorcycle video generation
    
    Workflow:
        CSV Feed → Parse → Download Images → Process Images → 
        Generate Script → Create Voiceover → Generate QR → Compose Video
    """

    def __init__(
        self,
        csv_path: str = "sample-feed.csv",
        assets_dir: str = "./assets",
        output_dir: str = "./output",
        template: str = "dark"
    ):
        self.csv_path = csv_path
        self.assets_dir = Path(assets_dir)
        self.output_dir = Path(output_dir)
        self.template = template

        # Create directories
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        logger.info("Initializing pipeline components...")
        
        # Data layer
        self.feed_parser = FeedParser(csv_path)
        self.image_downloader = ImageDownloader(assets_dir=str(self.assets_dir))
        self.asset_manager = AssetManager(assets_dir=str(self.assets_dir))
        
        # AI layer
        self.script_generator = ScriptGenerator(provider="openai")
        self.voice_generator = VoiceGenerator(provider="gtts", default_style="aggressive")
        self.qr_generator = QRGenerator()
        self.image_processor = ImageProcessor()
        
        # Video layer
        self.video_composer = VideoComposer(
            template=template,
            resolution=(1920, 1080),
            fps=30,
            duration=30.0,
            output_dir=str(self.output_dir)
        )

        logger.info("Pipeline initialized successfully")

    # ==================== PHASE 1: DATA INGESTION ====================
    
    def phase1_parse_feed(self, limit: Optional[int] = None) -> List[MotorcycleListing]:
        """Parse CSV feed and return listings"""
        logger.info("\n" + "="*60)
        logger.info("PHASE 1: DATA INGESTION")
        logger.info("="*60)
        
        listings = self.feed_parser.parse()
        
        if limit:
            listings = listings[:limit]
        
        logger.info(f"Parsed {len(listings)} listings from {self.csv_path}")
        
        for listing in listings[:3]:
            logger.info(f"  - {listing.display_name} (${listing.price:,.0f})")
        
        if len(listings) > 3:
            logger.info(f"  ... and {len(listings) - 3} more")
        
        return listings

    def phase1_download_images(self, listings: List[MotorcycleListing]) -> dict:
        """Download all images for listings"""
        logger.info("\nDownloading images...")
        results = self.image_downloader.download_batch(listings)
        
        total_images = sum(len(paths) for paths in results.values())
        logger.info(f"Downloaded {total_images} images for {len(results)} listings")
        
        return results

    def phase1_save_metadata(self, listings: List[MotorcycleListing]):
        """Save listing metadata to JSON"""
        logger.info("\nSaving metadata...")
        for listing in listings:
            self.asset_manager.save_listing_metadata(listing)
        logger.info(f"Saved metadata for {len(listings)} listings")

    # ==================== PHASE 2: AI GENERATION ====================
    
    def phase2_process_images(self, listings: List[MotorcycleListing]):
        """Process images with AI background removal"""
        logger.info("\n" + "="*60)
        logger.info("PHASE 2: AI GENERATION - Image Processing")
        logger.info("="*60)
        
        for listing in listings:
            listing_dir = self.asset_manager.get_listing_dir(listing)
            photo_files = sorted(listing_dir.glob("photo_*.jpg"))
            
            if not photo_files:
                logger.warning(f"No photos for {listing.stock_number}")
                continue
            
            # Create output directory (use v2_output for best quality)
            processed_dir = listing_dir / "v2_output"
            
            # Skip if already processed
            if processed_dir.exists() and len(list(processed_dir.glob("*.png"))) >= len(photo_files):
                logger.info(f"Images already processed for {listing.stock_number}, skipping...")
                continue
            
            processed_dir.mkdir(exist_ok=True)
            
            # Process each photo
            logger.info(f"\nProcessing {len(photo_files)} images for {listing.stock_number}...")
            
            stats = self.image_processor.process_batch(
                input_dir=str(listing_dir),
                output_dir=str(processed_dir),
                pattern="photo_*.jpg"
            )
            
            logger.info(f"  Processed: {stats['success']}/{stats['total']}")

    def phase2_generate_scripts(self, listings: List[MotorcycleListing]):
        """Generate ad scripts for each listing"""
        logger.info("\n" + "-"*40)
        logger.info("Generating Scripts...")
        logger.info("-"*40)
        
        for listing in listings:
            try:
                script = self.script_generator.generate_script(
                    year=listing.year,
                    make=listing.make,
                    model=listing.model,
                    price=listing.price,
                    description=listing.description,
                    color=listing.color,
                    mileage=listing.odometer,
                    engine=listing.engine_displacement,
                    is_custom=listing.is_custom,
                    style="aggressive"
                )
                
                # Save script
                script_path = self.asset_manager.get_script_path(listing)
                script_path.parent.mkdir(parents=True, exist_ok=True)
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(script)
                
                logger.info(f"  [OK] Script for {listing.stock_number}")
                
            except Exception as e:
                logger.error(f"  [FAIL] Script for {listing.stock_number}: {e}")

    def phase2_generate_voiceovers(self, listings: List[MotorcycleListing]):
        """Generate voiceovers from scripts"""
        logger.info("\n" + "-"*40)
        logger.info("Generating Voiceovers...")
        logger.info("-"*40)
        
        for listing in listings:
            try:
                script_path = self.asset_manager.get_script_path(listing)
                if not script_path.exists():
                    logger.warning(f"  No script for {listing.stock_number}")
                    continue
                
                voiceover_path = self.asset_manager.get_audio_path(listing, "voiceover")
                
                # Skip if valid voiceover already exists
                if voiceover_path.exists() and voiceover_path.stat().st_size > 5000:
                    duration = self.voice_generator.get_audio_duration(str(voiceover_path))
                    if duration and duration > 5:
                        logger.info(f"  [SKIP] Voiceover exists for {listing.stock_number} ({duration:.1f}s)")
                        continue
                
                success = self.voice_generator.generate_from_script_file(
                    script_path=str(script_path),
                    output_path=str(voiceover_path),
                    style="aggressive"
                )
                
                if success:
                    duration = self.voice_generator.get_audio_duration(str(voiceover_path))
                    if duration:
                        logger.info(f"  [OK] Voiceover for {listing.stock_number} ({duration:.1f}s)")
                    else:
                        logger.info(f"  [OK] Voiceover for {listing.stock_number}")
                else:
                    logger.error(f"  [FAIL] Voiceover for {listing.stock_number}")
                    
            except Exception as e:
                logger.error(f"  [FAIL] Voiceover for {listing.stock_number}: {e}")

    def phase2_generate_qr_codes(self, listings: List[MotorcycleListing]):
        """Generate QR codes for listings"""
        logger.info("\n" + "-"*40)
        logger.info("Generating QR Codes...")
        logger.info("-"*40)
        
        for listing in listings:
            try:
                if listing.listing_url:
                    qr_path = self.asset_manager.get_qr_code_path(listing)
                    self.qr_generator.generate_qr_code(
                        url=listing.listing_url,
                        output_path=qr_path,
                        size=(400, 400)
                    )
                    logger.info(f"  [OK] QR code for {listing.stock_number}")
                else:
                    logger.warning(f"  No URL for {listing.stock_number}")
                    
            except Exception as e:
                logger.error(f"  [FAIL] QR code for {listing.stock_number}: {e}")

    # ==================== PHASE 3: VIDEO PRODUCTION ====================
    
    def phase3_create_videos(self, listings: List[MotorcycleListing], background_music: Optional[str] = None):
        """Create videos for all listings"""
        logger.info("\n" + "="*60)
        logger.info("PHASE 3: VIDEO PRODUCTION")
        logger.info("="*60)
        
        videos_created = []
        
        for listing in listings:
            try:
                listing_dir = self.asset_manager.get_listing_dir(listing)
                
                # Check required assets - try v2_output first, then processed
                processed_dir = listing_dir / "v2_output"
                if not processed_dir.exists():
                    processed_dir = listing_dir / "processed"
                
                bike_images = list(processed_dir.glob("*.png"))
                voiceover = listing_dir / "voiceover.mp3"
                qr_code = listing_dir / "qr_code.png"
                
                if not bike_images:
                    logger.warning(f"  No processed images for {listing.stock_number}")
                    continue
                
                if not voiceover.exists():
                    logger.warning(f"  No voiceover for {listing.stock_number}")
                    continue
                
                # Prepare bike data
                bike_data = {
                    'year': listing.year,
                    'make': listing.make,
                    'model': listing.model,
                    'price': listing.price,
                    'stock_number': listing.stock_number,
                    'dealer_name': 'San Diego Harley-Davidson',
                    'color': listing.color,
                    'mileage': listing.odometer,
                    'engine': listing.engine_displacement
                }
                
                # Create video
                logger.info(f"\nCreating video for {listing.stock_number}...")
                
                video_path = self.video_composer.create_video(
                    bike_data=bike_data,
                    bike_image=str(bike_images[0]),
                    voiceover=str(voiceover),
                    qr_code=str(qr_code) if qr_code.exists() else None,
                    background_music=background_music
                )
                
                videos_created.append(video_path)
                logger.info(f"  [OK] Video created: {video_path}")
                
            except Exception as e:
                logger.error(f"  [FAIL] Video for {listing.stock_number}: {e}")
        
        return videos_created

    # ==================== FULL PIPELINE ====================
    
    def run(self, limit: Optional[int] = None, skip_video: bool = False):
        """
        Run complete pipeline
        
        Args:
            limit: Limit number of listings to process
            skip_video: Skip video generation (assets only)
        """
        logger.info("\n" + "="*60)
        logger.info("SLASHER TV AI - VIDEO GENERATION PIPELINE")
        logger.info("="*60)
        
        # Phase 1: Data Ingestion
        listings = self.phase1_parse_feed(limit)
        self.phase1_download_images(listings)
        self.phase1_save_metadata(listings)
        
        # Phase 2: AI Generation
        self.phase2_process_images(listings)
        self.phase2_generate_scripts(listings)
        self.phase2_generate_voiceovers(listings)
        self.phase2_generate_qr_codes(listings)
        
        # Phase 3: Video Production
        if not skip_video:
            videos = self.phase3_create_videos(listings)
            logger.info(f"\nCreated {len(videos)} videos")
        
        # Summary
        self._print_summary(listings)
        
        logger.info("\n" + "="*60)
        logger.info("PIPELINE COMPLETE!")
        logger.info("="*60)

    def _print_summary(self, listings: List[MotorcycleListing]):
        """Print pipeline summary"""
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        
        for listing in listings:
            summary = self.asset_manager.get_asset_summary(listing)
            print(f"\n{listing.display_name}")
            print(f"  Stock: {listing.stock_number}")
            print(f"  Price: ${listing.price:,.0f}")
            print(f"  Images: {summary['images']} → Processed: {summary['processed_images']}")
            print(f"  Script: {'✓' if summary['has_script'] else '✗'}")
            print(f"  Voiceover: {'✓' if summary['has_voiceover'] else '✗'}")
            print(f"  QR Code: {'✓' if summary['has_qr_code'] else '✗'}")
        
        print(f"\nAssets: {self.assets_dir}")
        print(f"Output: {self.output_dir}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Slasher TV AI - Motorcycle Video Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main                      # Process all listings
  python -m src.main --limit 1            # Process first listing only
  python -m src.main --skip-video         # Generate assets only (no video)
  python -m src.main --template dark      # Use dark template
        """
    )
    
    parser.add_argument("--csv", default="sample-feed.csv", help="CSV feed path")
    parser.add_argument("--limit", type=int, help="Limit listings to process")
    parser.add_argument("--assets-dir", default="./assets", help="Assets directory")
    parser.add_argument("--output-dir", default="./output", help="Output directory")
    parser.add_argument("--template", default="dark", choices=["dark", "clean", "fire"], help="Video template")
    parser.add_argument("--skip-video", action="store_true", help="Skip video generation")
    
    args = parser.parse_args()
    
    # Create and run pipeline
    pipeline = SlasherTVPipeline(
        csv_path=args.csv,
        assets_dir=args.assets_dir,
        output_dir=args.output_dir,
        template=args.template
    )
    
    pipeline.run(limit=args.limit, skip_video=args.skip_video)


if __name__ == "__main__":
    main()
