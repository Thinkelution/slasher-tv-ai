"""
Cloudflare R2 Uploader for Slasher TV AI
Upload processed images and audio to R2 for sharing
"""

import os
import boto3
from botocore.config import Config
from pathlib import Path
from typing import Optional, Dict
import logging
import mimetypes
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class R2Uploader:
    """Upload assets to Cloudflare R2 and get shareable URLs"""
    
    def __init__(self):
        """Initialize R2 client with environment variables"""
        account_id = os.getenv("R2_ACCOUNT_ID")
        access_key = os.getenv("R2_ACCESS_KEY_ID")
        secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
        self.bucket_name = os.getenv("R2_BUCKET_NAME", "slasher-tv")
        self.public_url = os.getenv("R2_PUBLIC_URL")  # e.g., https://your-bucket.your-domain.com
        
        if not all([account_id, access_key, secret_key]):
            raise ValueError(
                "R2 credentials required. Set R2_ACCOUNT_ID, "
                "R2_ACCESS_KEY_ID, and R2_SECRET_ACCESS_KEY in .env"
            )
        
        # R2 endpoint
        endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"
        
        # Initialize S3 client for R2
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version="s3v4")
        )
        
        logger.info(f"R2 initialized for bucket: {self.bucket_name}")
    
    def upload_file(
        self,
        file_path: Path,
        key: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> Dict:
        """
        Upload a file to R2
        
        Args:
            file_path: Path to the file
            key: Object key (path in bucket). If None, uses filename
            content_type: MIME type. If None, auto-detected
            
        Returns:
            Dict with url and key
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Generate key from filename if not provided
        if not key:
            key = file_path.name
        
        # Auto-detect content type
        if not content_type:
            content_type, _ = mimetypes.guess_type(str(file_path))
            content_type = content_type or "application/octet-stream"
        
        try:
            # Upload file
            with open(file_path, "rb") as f:
                self.client.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=f,
                    ContentType=content_type
                )
            
            # Build public URL
            if self.public_url:
                url = f"{self.public_url.rstrip('/')}/{key}"
            else:
                url = f"https://{self.bucket_name}.r2.dev/{key}"
            
            logger.info(f"✓ Uploaded: {key}")
            
            return {
                "url": url,
                "key": key,
                "content_type": content_type,
                "size_bytes": file_path.stat().st_size
            }
            
        except Exception as e:
            logger.error(f"Failed to upload {file_path.name}: {e}")
            raise
    
    def upload_image(
        self,
        file_path: Path,
        folder: str = "images"
    ) -> Dict:
        """Upload an image to R2"""
        file_path = Path(file_path)
        key = f"{folder}/{file_path.name}"
        return self.upload_file(file_path, key=key)
    
    def upload_audio(
        self,
        file_path: Path,
        folder: str = "audio"
    ) -> Dict:
        """Upload an audio file to R2"""
        file_path = Path(file_path)
        key = f"{folder}/{file_path.name}"
        return self.upload_file(file_path, key=key, content_type="audio/mpeg")
    
    def upload_listing_assets(
        self,
        listing_dir: Path,
        stock_number: str
    ) -> Dict:
        """
        Upload all assets for a listing to R2
        
        Args:
            listing_dir: Directory containing listing assets
            stock_number: Stock number for folder organization
            
        Returns:
            Dict with URLs for all uploaded assets
        """
        listing_dir = Path(listing_dir)
        folder = f"listings/{stock_number}"
        
        results = {
            "processed_images": [],
            "voiceover": None,
            "qr_code": None
        }
        
        # Upload processed images
        processed_dir = listing_dir / "processed"
        if processed_dir.exists():
            for img_path in processed_dir.glob("*_nobg.png"):
                try:
                    key = f"{folder}/processed/{img_path.name}"
                    result = self.upload_file(img_path, key=key)
                    results["processed_images"].append(result)
                except Exception as e:
                    logger.warning(f"Failed to upload {img_path.name}: {e}")
        
        # Upload voiceover
        voiceover_path = listing_dir / "voiceover.mp3"
        if voiceover_path.exists():
            try:
                key = f"{folder}/voiceover.mp3"
                results["voiceover"] = self.upload_file(
                    voiceover_path, 
                    key=key,
                    content_type="audio/mpeg"
                )
            except Exception as e:
                logger.warning(f"Failed to upload voiceover: {e}")
        
        # Upload QR code
        qr_path = listing_dir / "qr_code.png"
        if qr_path.exists():
            try:
                key = f"{folder}/qr_code.png"
                results["qr_code"] = self.upload_file(qr_path, key=key)
            except Exception as e:
                logger.warning(f"Failed to upload QR code: {e}")
        
        logger.info(f"Uploaded assets for stock #{stock_number}")
        return results


# Example usage
if __name__ == "__main__":
    uploader = R2Uploader()
    
    # Test upload
    test_dir = Path("assets/api/156359BB")
    if test_dir.exists():
        results = uploader.upload_listing_assets(test_dir, "156359BB")
        print("\nUpload Results:")
        print(f"  Processed Images: {len(results['processed_images'])}")
        for img in results['processed_images']:
            print(f"    - {img['url']}")
        if results['voiceover']:
            print(f"  Voiceover: {results['voiceover']['url']}")
        if results['qr_code']:
            print(f"  QR Code: {results['qr_code']['url']}")

