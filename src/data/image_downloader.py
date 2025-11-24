"""
Image Downloader for motorcycle photos from inventory feeds
"""

import requests
from pathlib import Path
from typing import List, Optional
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time

from .data_models import MotorcycleListing

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageDownloader:
    """Download and manage motorcycle images"""

    def __init__(
        self,
        assets_dir: str = "./assets",
        max_workers: int = 5,
        timeout: int = 30,
        retry_count: int = 3
    ):
        """
        Initialize image downloader

        Args:
            assets_dir: Base directory for storing assets
            max_workers: Maximum concurrent downloads
            timeout: Request timeout in seconds
            retry_count: Number of retry attempts
        """
        self.assets_dir = Path(assets_dir)
        self.max_workers = max_workers
        self.timeout = timeout
        self.retry_count = retry_count

        # Create assets directory
        self.assets_dir.mkdir(parents=True, exist_ok=True)

    def download_listing_images(
        self,
        listing: MotorcycleListing,
        force: bool = False
    ) -> List[Path]:
        """
        Download all images for a single listing

        Args:
            listing: MotorcycleListing object
            force: Force re-download even if files exist

        Returns:
            List of paths to downloaded images
        """
        # Create listing directory
        listing_dir = self._get_listing_dir(listing)
        listing_dir.mkdir(parents=True, exist_ok=True)

        downloaded_paths = []

        for idx, url in enumerate(listing.photo_urls):
            try:
                # Generate filename
                filename = f"photo_{idx:02d}.jpg"
                output_path = listing_dir / filename

                # Skip if already exists and not forcing
                if output_path.exists() and not force:
                    logger.debug(f"Image already exists: {output_path}")
                    downloaded_paths.append(output_path)
                    continue

                # Download image
                success = self._download_image(url, output_path)
                if success:
                    downloaded_paths.append(output_path)
                    logger.info(f"Downloaded: {filename} for stock #{listing.stock_number}")

            except Exception as e:
                logger.warning(f"Failed to download image {idx} for {listing.stock_number}: {e}")
                continue

        return downloaded_paths

    def download_batch(
        self,
        listings: List[MotorcycleListing],
        force: bool = False
    ) -> dict:
        """
        Download images for multiple listings in parallel

        Args:
            listings: List of MotorcycleListing objects
            force: Force re-download even if files exist

        Returns:
            Dictionary mapping stock_number to downloaded image paths
        """
        results = {}

        logger.info(f"Starting batch download for {len(listings)} listings...")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all download tasks
            future_to_listing = {
                executor.submit(self.download_listing_images, listing, force): listing
                for listing in listings
            }

            # Process completed downloads with progress bar
            with tqdm(total=len(listings), desc="Downloading images") as pbar:
                for future in as_completed(future_to_listing):
                    listing = future_to_listing[future]
                    try:
                        paths = future.result()
                        results[listing.stock_number] = paths
                        logger.info(f"Completed {listing.stock_number}: {len(paths)} images")
                    except Exception as e:
                        logger.error(f"Failed to download images for {listing.stock_number}: {e}")
                        results[listing.stock_number] = []
                    finally:
                        pbar.update(1)

        logger.info(f"Batch download complete. Processed {len(results)} listings.")
        return results

    def _download_image(self, url: str, output_path: Path) -> bool:
        """
        Download single image with retry logic

        Args:
            url: Image URL
            output_path: Path to save image

        Returns:
            True if successful, False otherwise
        """
        for attempt in range(self.retry_count):
            try:
                # Add headers to mimic browser
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }

                # Download image
                response = requests.get(
                    url,
                    headers=headers,
                    timeout=self.timeout,
                    stream=True
                )
                response.raise_for_status()

                # Save to file
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                return True

            except requests.exceptions.RequestException as e:
                logger.warning(f"Download attempt {attempt + 1} failed for {url}: {e}")
                if attempt < self.retry_count - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                continue

        return False

    def _get_listing_dir(self, listing: MotorcycleListing) -> Path:
        """
        Get directory path for listing assets

        Args:
            listing: MotorcycleListing object

        Returns:
            Path to listing directory
        """
        return self.assets_dir / listing.dealer_id / listing.stock_number

    def get_listing_images(self, listing: MotorcycleListing) -> List[Path]:
        """
        Get list of downloaded images for a listing

        Args:
            listing: MotorcycleListing object

        Returns:
            List of image paths
        """
        listing_dir = self._get_listing_dir(listing)
        if not listing_dir.exists():
            return []

        # Get all .jpg files
        images = sorted(listing_dir.glob("photo_*.jpg"))
        return images

    def cleanup_listing(self, listing: MotorcycleListing):
        """
        Remove all downloaded assets for a listing

        Args:
            listing: MotorcycleListing object
        """
        listing_dir = self._get_listing_dir(listing)
        if listing_dir.exists():
            import shutil
            shutil.rmtree(listing_dir)
            logger.info(f"Cleaned up assets for {listing.stock_number}")


# Example usage
if __name__ == "__main__":
    from .feed_parser import FeedParser

    # Parse feed
    parser = FeedParser("sample-feed.csv")
    listings = parser.parse()

    # Download images for first 3 listings
    downloader = ImageDownloader(assets_dir="./assets", max_workers=3)
    results = downloader.download_batch(listings[:3])

    print(f"\nDownload results:")
    for stock_num, paths in results.items():
        print(f"  {stock_num}: {len(paths)} images")
