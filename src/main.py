"""
Main entry point for Slasher TV AI video generation
"""

import os
import sys
from pathlib import Path
import logging
from typing import List, Optional
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data import FeedParser, ImageDownloader, AssetManager, MotorcycleListing
from src.ai import ScriptGenerator, QRGenerator

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SlasherTVPipeline:
    """Main pipeline for video generation"""

    def __init__(
        self,
        csv_path: str = "sample-feed.csv",
        assets_dir: str = "./assets",
        output_dir: str = "./output"
    ):
        """
        Initialize pipeline

        Args:
            csv_path: Path to inventory CSV
            assets_dir: Assets directory
            output_dir: Output directory for videos
        """
        self.csv_path = csv_path
        self.assets_dir = Path(assets_dir)
        self.output_dir = Path(output_dir)

        # Create directories
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.feed_parser = FeedParser(csv_path)
        self.image_downloader = ImageDownloader(assets_dir=str(self.assets_dir))
        self.asset_manager = AssetManager(assets_dir=str(self.assets_dir))
        self.script_generator = ScriptGenerator(provider="openai")
        self.qr_generator = QRGenerator()

        logger.info("Slasher TV Pipeline initialized")

    def run_pipeline(self, limit: Optional[int] = None):
        """
        Run full pipeline for generating videos

        Args:
            limit: Limit number of listings to process (None for all)
        """
        logger.info("=" * 50)
        logger.info("Starting Slasher TV AI Pipeline")
        logger.info("=" * 50)

        # Step 1: Parse feed
        logger.info("\n[1/5] Parsing inventory feed...")
        listings = self.feed_parser.parse()

        if limit:
            listings = listings[:limit]

        logger.info(f"Loaded {len(listings)} listings")

        # Step 2: Download images
        logger.info("\n[2/5] Downloading images...")
        download_results = self.image_downloader.download_batch(listings)

        # Step 3: Save metadata
        logger.info("\n[3/5] Saving metadata...")
        for listing in listings:
            self.asset_manager.save_listing_metadata(listing)

        # Step 4: Generate scripts and QR codes
        logger.info("\n[4/5] Generating scripts and QR codes...")
        for listing in listings:
            try:
                # Generate script
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

                logger.info(f"Generated script for {listing.stock_number}")

                # Generate QR code
                if listing.listing_url:
                    qr_path = self.asset_manager.get_qr_code_path(listing)
                    self.qr_generator.generate_qr_code(
                        url=listing.listing_url,
                        output_path=qr_path,
                        size=(400, 400)
                    )
                    logger.info(f"Generated QR code for {listing.stock_number}")

            except Exception as e:
                logger.error(f"Failed to process {listing.stock_number}: {e}")
                continue

        # Step 5: Ready for video generation
        logger.info("\n[5/5] Assets ready for video generation")
        logger.info(f"\nProcessed {len(listings)} listings")
        logger.info(f"Assets saved to: {self.assets_dir}")
        logger.info(f"Videos will be saved to: {self.output_dir}")

        logger.info("\n" + "=" * 50)
        logger.info("Pipeline complete!")
        logger.info("=" * 50)

        # Print summary
        self._print_summary(listings)

    def _print_summary(self, listings: List[MotorcycleListing]):
        """Print pipeline summary"""
        print("\n\nPIPELINE SUMMARY")
        print("=" * 60)

        for listing in listings[:5]:  # Show first 5
            summary = self.asset_manager.get_asset_summary(listing)
            print(f"\n{listing.display_name}")
            print(f"  Stock: {listing.stock_number}")
            print(f"  Price: ${listing.price:,.0f}")
            print(f"  Images: {summary['images']}")
            print(f"  Script: {'✓' if summary['has_script'] else '✗'}")
            print(f"  QR Code: {'✓' if summary['has_qr_code'] else '✗'}")

        if len(listings) > 5:
            print(f"\n... and {len(listings) - 5} more listings")

    def process_single_listing(self, stock_number: str):
        """
        Process a single listing by stock number

        Args:
            stock_number: Stock number to process
        """
        logger.info(f"Processing single listing: {stock_number}")

        # Parse feed and find listing
        listings = self.feed_parser.parse()
        listing = next((l for l in listings if l.stock_number == stock_number), None)

        if not listing:
            logger.error(f"Listing not found: {stock_number}")
            return

        # Download images
        images = self.image_downloader.download_listing_images(listing)
        logger.info(f"Downloaded {len(images)} images")

        # Save metadata
        self.asset_manager.save_listing_metadata(listing)

        # Generate script
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
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script)

        print(f"\n{listing.display_name}")
        print(f"Price: ${listing.price:,.0f}")
        print(f"\nGenerated Script:")
        print("-" * 60)
        print(script)
        print("-" * 60)

        # Generate QR code
        if listing.listing_url:
            qr_path = self.asset_manager.get_qr_code_path(listing)
            self.qr_generator.generate_qr_code(
                url=listing.listing_url,
                output_path=qr_path
            )

        logger.info(f"Processing complete for {stock_number}")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Slasher TV AI Video Generator")
    parser.add_argument(
        "--csv",
        default="sample-feed.csv",
        help="Path to inventory CSV feed"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of listings to process"
    )
    parser.add_argument(
        "--stock",
        type=str,
        help="Process single listing by stock number"
    )
    parser.add_argument(
        "--assets-dir",
        default="./assets",
        help="Assets directory"
    )
    parser.add_argument(
        "--output-dir",
        default="./output",
        help="Output directory for videos"
    )

    args = parser.parse_args()

    # Create pipeline
    pipeline = SlasherTVPipeline(
        csv_path=args.csv,
        assets_dir=args.assets_dir,
        output_dir=args.output_dir
    )

    # Process single or batch
    if args.stock:
        pipeline.process_single_listing(args.stock)
    else:
        pipeline.run_pipeline(limit=args.limit)


if __name__ == "__main__":
    main()
