"""
Asset Manager for organizing and managing video generation assets
"""

import json
from pathlib import Path
from typing import List, Optional, Dict
import logging

from .data_models import MotorcycleListing, VideoMetadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AssetManager:
    """Manage assets and metadata for video generation"""

    def __init__(self, assets_dir: str = "./assets"):
        """
        Initialize asset manager

        Args:
            assets_dir: Base directory for assets
        """
        self.assets_dir = Path(assets_dir)
        self.assets_dir.mkdir(parents=True, exist_ok=True)

    def get_listing_dir(self, listing: MotorcycleListing) -> Path:
        """Get directory path for listing"""
        return self.assets_dir / listing.dealer_id / listing.stock_number

    def save_listing_metadata(self, listing: MotorcycleListing):
        """
        Save listing metadata to JSON

        Args:
            listing: MotorcycleListing object
        """
        listing_dir = self.get_listing_dir(listing)
        listing_dir.mkdir(parents=True, exist_ok=True)

        metadata_path = listing_dir / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(listing.model_dump(), f, indent=2, default=str)

        logger.info(f"Saved metadata for {listing.stock_number}")

    def load_listing_metadata(self, dealer_id: str, stock_number: str) -> Optional[MotorcycleListing]:
        """
        Load listing metadata from JSON

        Args:
            dealer_id: Dealer identifier
            stock_number: Stock number

        Returns:
            MotorcycleListing object or None
        """
        metadata_path = self.assets_dir / dealer_id / stock_number / "metadata.json"
        if not metadata_path.exists():
            return None

        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return MotorcycleListing(**data)
        except Exception as e:
            logger.error(f"Failed to load metadata from {metadata_path}: {e}")
            return None

    def save_video_metadata(self, video_meta: VideoMetadata):
        """
        Save video generation metadata

        Args:
            video_meta: VideoMetadata object
        """
        listing_dir = self.get_listing_dir(video_meta.listing)
        video_meta_path = listing_dir / "video_metadata.json"

        with open(video_meta_path, 'w', encoding='utf-8') as f:
            json.dump(video_meta.model_dump(), f, indent=2, default=str)

        logger.info(f"Saved video metadata for {video_meta.listing.stock_number}")

    def get_images(self, listing: MotorcycleListing) -> List[Path]:
        """
        Get all downloaded images for a listing

        Args:
            listing: MotorcycleListing object

        Returns:
            List of image paths
        """
        listing_dir = self.get_listing_dir(listing)
        if not listing_dir.exists():
            return []

        images = sorted(listing_dir.glob("photo_*.jpg"))
        return images

    def get_processed_image(self, listing: MotorcycleListing, image_idx: int = 0) -> Optional[Path]:
        """
        Get processed (background removed) image from processed subfolder

        Args:
            listing: MotorcycleListing object
            image_idx: Image index

        Returns:
            Path to processed image or None
        """
        listing_dir = self.get_listing_dir(listing)
        processed_dir = listing_dir / "processed"
        
        # Look for processed image in processed subfolder
        processed_path = processed_dir / f"photo_{image_idx:02d}_nobg.png"
        if processed_path.exists():
            return processed_path
        
        # Fallback: check old naming convention
        old_path = listing_dir / f"processed_{image_idx:02d}.png"
        if old_path.exists():
            return old_path
            
        return None

    def get_processed_dir(self, listing: MotorcycleListing) -> Path:
        """
        Get processed images directory for listing

        Args:
            listing: MotorcycleListing object

        Returns:
            Path to processed directory
        """
        listing_dir = self.get_listing_dir(listing)
        processed_dir = listing_dir / "processed"
        processed_dir.mkdir(parents=True, exist_ok=True)
        return processed_dir

    def get_all_processed_images(self, listing: MotorcycleListing) -> List[Path]:
        """
        Get all processed images for a listing

        Args:
            listing: MotorcycleListing object

        Returns:
            List of paths to processed images
        """
        listing_dir = self.get_listing_dir(listing)
        processed_dir = listing_dir / "processed"
        
        if not processed_dir.exists():
            return []
        
        return sorted(processed_dir.glob("*_nobg.png"))

    def set_processed_image_path(
        self,
        listing: MotorcycleListing,
        image_idx: int
    ) -> Path:
        """
        Get path for saving processed image

        Args:
            listing: MotorcycleListing object
            image_idx: Image index

        Returns:
            Path where processed image should be saved
        """
        processed_dir = self.get_processed_dir(listing)
        return processed_dir / f"photo_{image_idx:02d}_nobg.png"

    def get_qr_code_path(self, listing: MotorcycleListing) -> Path:
        """
        Get path for QR code image

        Args:
            listing: MotorcycleListing object

        Returns:
            Path to QR code image
        """
        listing_dir = self.get_listing_dir(listing)
        return listing_dir / "qr_code.png"

    def get_audio_path(self, listing: MotorcycleListing, audio_type: str = "voiceover") -> Path:
        """
        Get path for audio file

        Args:
            listing: MotorcycleListing object
            audio_type: Type of audio (voiceover, music, etc.)

        Returns:
            Path to audio file
        """
        listing_dir = self.get_listing_dir(listing)
        return listing_dir / f"{audio_type}.mp3"

    def get_script_path(self, listing: MotorcycleListing) -> Path:
        """
        Get path for script text file

        Args:
            listing: MotorcycleListing object

        Returns:
            Path to script file
        """
        listing_dir = self.get_listing_dir(listing)
        return listing_dir / "script.txt"

    def list_all_listings(self) -> List[Dict[str, str]]:
        """
        List all listings with downloaded assets

        Returns:
            List of dicts with dealer_id and stock_number
        """
        listings = []

        for dealer_dir in self.assets_dir.iterdir():
            if not dealer_dir.is_dir():
                continue

            for stock_dir in dealer_dir.iterdir():
                if not stock_dir.is_dir():
                    continue

                # Check if has metadata
                metadata_path = stock_dir / "metadata.json"
                if metadata_path.exists():
                    listings.append({
                        'dealer_id': dealer_dir.name,
                        'stock_number': stock_dir.name,
                        'path': str(stock_dir)
                    })

        return listings

    def get_asset_summary(self, listing: MotorcycleListing) -> Dict:
        """
        Get summary of available assets for a listing

        Args:
            listing: MotorcycleListing object

        Returns:
            Dictionary with asset counts and paths
        """
        listing_dir = self.get_listing_dir(listing)
        processed_dir = listing_dir / "processed"

        # Count processed images in processed subfolder
        processed_count = 0
        if processed_dir.exists():
            processed_count = len(list(processed_dir.glob("*_nobg.png")))

        summary = {
            'listing_dir': str(listing_dir),
            'images': len(list(listing_dir.glob("photo_*.jpg"))),
            'processed_images': processed_count,
            'processed_dir': str(processed_dir) if processed_dir.exists() else None,
            'has_qr_code': (listing_dir / "qr_code.png").exists(),
            'has_voiceover': (listing_dir / "voiceover.mp3").exists(),
            'has_script': (listing_dir / "script.txt").exists(),
            'has_metadata': (listing_dir / "metadata.json").exists(),
            'has_video_metadata': (listing_dir / "video_metadata.json").exists(),
        }

        return summary


# Example usage
if __name__ == "__main__":
    from .feed_parser import FeedParser

    # Parse feed
    parser = FeedParser("sample-feed.csv")
    listings = parser.parse()

    if listings:
        # Initialize asset manager
        asset_mgr = AssetManager(assets_dir="./assets")

        # Save metadata for first listing
        first_listing = listings[0]
        asset_mgr.save_listing_metadata(first_listing)

        # Get asset summary
        summary = asset_mgr.get_asset_summary(first_listing)
        print(f"\nAsset summary for {first_listing.stock_number}:")
        for key, value in summary.items():
            print(f"  {key}: {value}")
