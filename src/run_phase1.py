"""
Phase 1: Data Pipeline Layer - Execute for single bike
Parses CSV, downloads images, saves metadata
"""

import sys
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data import FeedParser, ImageDownloader, AssetManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_phase1(csv_path: str = "sample-feed.csv", limit: int = 1):
    """
    Execute Phase 1: Data Ingestion Pipeline
    
    1. Load CSV feed
    2. Parse motorcycle listing
    3. Download all images
    4. Store in organized directory structure
    5. Generate metadata JSON
    """
    logger.info("=" * 60)
    logger.info("PHASE 1: DATA PIPELINE LAYER")
    logger.info("=" * 60)
    
    # Initialize components
    parser = FeedParser(csv_path)
    downloader = ImageDownloader(assets_dir="./assets", max_workers=3)
    asset_manager = AssetManager(assets_dir="./assets")
    
    # Step 1: Parse feed
    logger.info("\n[Step 1/4] Parsing CSV feed...")
    listings = parser.parse()
    listings = listings[:limit]  # Limit to specified number
    
    if not listings:
        logger.error("No listings found in feed!")
        return
    
    listing = listings[0]
    logger.info(f"Selected: {listing.display_name}")
    logger.info(f"  Stock #: {listing.stock_number}")
    logger.info(f"  Price: ${listing.price:,.0f}")
    logger.info(f"  Photos available: {len(listing.photo_urls)}")
    
    # Step 2: Create directory structure
    logger.info("\n[Step 2/4] Creating directory structure...")
    listing_dir = asset_manager.get_listing_dir(listing)
    listing_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"  Created: {listing_dir}")
    
    # Step 3: Download images
    logger.info("\n[Step 3/4] Downloading images...")
    downloaded_paths = downloader.download_listing_images(listing)
    logger.info(f"  Downloaded {len(downloaded_paths)} images")
    
    # Step 4: Save metadata
    logger.info("\n[Step 4/4] Saving metadata JSON...")
    asset_manager.save_listing_metadata(listing)
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("PHASE 1 COMPLETE")
    logger.info("=" * 60)
    
    print(f"\n📂 OUTPUT STRUCTURE:")
    print(f"   {listing_dir}/")
    
    # List files in directory
    for file in sorted(listing_dir.iterdir()):
        size = file.stat().st_size / 1024
        print(f"   ├── {file.name} ({size:.1f} KB)")
    
    print(f"\n🏍️  LISTING INFO:")
    print(f"   {listing.display_name}")
    print(f"   Stock #: {listing.stock_number}")
    print(f"   Price: ${listing.price:,.0f}")
    print(f"   Condition: {listing.condition}")
    if listing.color:
        print(f"   Color: {listing.color}")
    if listing.odometer:
        print(f"   Mileage: {listing.odometer:,} miles")
    
    print(f"\n📸 IMAGES: {len(downloaded_paths)} downloaded")
    for idx, path in enumerate(downloaded_paths[:5]):  # Show first 5
        print(f"   {idx+1}. {path.name}")
    if len(downloaded_paths) > 5:
        print(f"   ... and {len(downloaded_paths) - 5} more")
    
    return listing, downloaded_paths


if __name__ == "__main__":
    import argparse
    
    argparser = argparse.ArgumentParser(description="Phase 1: Data Pipeline")
    argparser.add_argument("--csv", default="sample-feed.csv", help="CSV feed path")
    argparser.add_argument("--limit", type=int, default=1, help="Number of listings")
    
    args = argparser.parse_args()
    run_phase1(csv_path=args.csv, limit=args.limit)

