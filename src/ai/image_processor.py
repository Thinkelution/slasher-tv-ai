"""
Image Processor using Removal.AI API
Professional background removal for motorcycle product images
"""

import os
import requests
from pathlib import Path
from typing import Optional, List, Union, Literal
from PIL import Image
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Removal.AI API Configuration
REMOVALAI_API_URL = "https://api.removal.ai/3.0/remove"


class OutputFormat(str, Enum):
    """Supported output formats for processed images"""
    PNG = "png"      # Transparent background
    JPG = "jpg"      # White background
    WEBP = "webp"    # Modern format with transparency


@dataclass
class ProcessingResult:
    """Result of image processing operation"""
    success: bool
    input_path: Path
    output_path: Optional[Path]
    file_size_kb: Optional[float]
    error: Optional[str] = None


class ImageProcessor:
    """
    Professional image processor using Removal.AI API
    
    Features:
    - High-quality background removal for product images
    - Transparent PNG output for video compositing
    - Fast batch processing with parallel execution (5 concurrent)
    - Organized output in 'processed' subfolder
    - Multiple output format support
    - Image optimization and resizing
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        output_format: OutputFormat = OutputFormat.PNG,
        max_workers: int = 5  # Increased for faster processing
    ):
        """
        Initialize image processor with Removal.AI

        Args:
            api_key: Removal.AI API key (or use REMOVALAI_API_KEY env var)
            output_format: Output format (png/jpg/webp)
            max_workers: Max concurrent API requests (default: 5 for speed)
        """
        self.api_key = api_key or os.getenv("REMOVALAI_API_KEY")
        if not self.api_key:
            raise ValueError("Removal.AI API key required. Set REMOVALAI_API_KEY env variable.")

        self.output_format = output_format
        self.max_workers = max_workers
        logger.info(f"Initialized ImageProcessor (format: {output_format.value}, workers: {max_workers})")

    def remove_background(
        self,
        input_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        get_base64: bool = False
    ) -> ProcessingResult:
        """
        Remove background from a single image using Removal.AI

        Args:
            input_path: Path to input image
            output_path: Path for output (auto-generated if None)
            get_base64: Return base64 instead of saving file

        Returns:
            ProcessingResult with success status and paths
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            return ProcessingResult(
                success=False,
                input_path=input_path,
                output_path=None,
                file_size_kb=None,
                error=f"Input file not found: {input_path}"
            )

        # Generate output path if not provided
        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_nobg.{self.output_format.value}"
        else:
            output_path = Path(output_path)

        try:
            # Prepare API request
            headers = {
                "Rm-Token": self.api_key
            }

            # Read image file
            with open(input_path, "rb") as f:
                files = {
                    "image_file": (input_path.name, f, self._get_mime_type(input_path))
                }
                
                data = {
                    "get_base64": "1" if get_base64 else "0",
                    "output_format": self.output_format.value
                }

                logger.info(f"Processing: {input_path.name}...")
                response = requests.post(
                    REMOVALAI_API_URL,
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=60
                )
                response.raise_for_status()

            # Parse response
            result = response.json()

            if result.get("status") == "success" or "url" in result:
                # Download processed image from URL
                image_url = result.get("url") or result.get("image_url")
                
                if image_url:
                    img_response = requests.get(image_url, timeout=30)
                    img_response.raise_for_status()

                    # Save processed image
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_path, "wb") as f:
                        f.write(img_response.content)

                    file_size = output_path.stat().st_size / 1024

                    logger.info(f"✓ Background removed: {output_path.name} ({file_size:.1f} KB)")
                    
                    return ProcessingResult(
                        success=True,
                        input_path=input_path,
                        output_path=output_path,
                        file_size_kb=file_size
                    )
                else:
                    return ProcessingResult(
                        success=False,
                        input_path=input_path,
                        output_path=None,
                        file_size_kb=None,
                        error="No image URL in API response"
                    )
            else:
                error_msg = result.get("message", "Unknown API error")
                return ProcessingResult(
                    success=False,
                    input_path=input_path,
                    output_path=None,
                    file_size_kb=None,
                    error=error_msg
                )

        except requests.exceptions.HTTPError as e:
            error_msg = f"API error: {e}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg = f"API error: {error_detail.get('message', str(e))}"
                except:
                    pass
            logger.error(error_msg)
            return ProcessingResult(
                success=False,
                input_path=input_path,
                output_path=None,
                file_size_kb=None,
                error=error_msg
            )
        except Exception as e:
            logger.error(f"Failed to process {input_path.name}: {e}")
            return ProcessingResult(
                success=False,
                input_path=input_path,
                output_path=None,
                file_size_kb=None,
                error=str(e)
            )

    def process_batch(
        self,
        image_paths: List[Path],
        output_dir: Optional[Path] = None,
        skip_existing: bool = True
    ) -> List[ProcessingResult]:
        """
        Process multiple images in parallel

        Args:
            image_paths: List of image paths to process
            output_dir: Directory for outputs (same as input if None)
            skip_existing: Skip if output already exists

        Returns:
            List of ProcessingResult for each image
        """
        results = []
        to_process = []

        # Filter images to process
        for path in image_paths:
            if output_dir:
                output_path = output_dir / f"{path.stem}_nobg.{self.output_format.value}"
            else:
                output_path = path.parent / f"{path.stem}_nobg.{self.output_format.value}"

            if skip_existing and output_path.exists():
                logger.info(f"Skipping (exists): {output_path.name}")
                results.append(ProcessingResult(
                    success=True,
                    input_path=path,
                    output_path=output_path,
                    file_size_kb=output_path.stat().st_size / 1024
                ))
            else:
                to_process.append((path, output_path))

        if not to_process:
            logger.info("All images already processed!")
            return results

        logger.info(f"Processing {len(to_process)} images...")

        # Process in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_path = {
                executor.submit(self.remove_background, path, out): path
                for path, out in to_process
            }

            for future in as_completed(future_to_path):
                result = future.result()
                results.append(result)

        # Summary
        success_count = sum(1 for r in results if r.success)
        logger.info(f"Batch complete: {success_count}/{len(results)} successful")

        return results

    def process_listing_images(
        self,
        listing_dir: Path,
        process_all: bool = True,
        max_images: Optional[int] = None
    ) -> List[ProcessingResult]:
        """
        Process all images for a motorcycle listing
        Saves to 'processed' subfolder

        Args:
            listing_dir: Directory containing listing images
            process_all: Process all images (default: True)
            max_images: Maximum number of images to process (None = all)

        Returns:
            List of ProcessingResult
        """
        listing_dir = Path(listing_dir)
        
        # Create 'processed' subfolder for outputs
        processed_dir = listing_dir / "processed"
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all original images (photo_00.jpg to photo_XX.jpg)
        image_files = sorted(listing_dir.glob("photo_*.jpg"))
        
        if not image_files:
            logger.warning(f"No images found in {listing_dir}")
            return []

        # Select images to process
        if max_images and not process_all:
            selected = image_files[:max_images]
        else:
            selected = image_files  # Process ALL images
            
        logger.info(f"Processing {len(selected)} images → {processed_dir}")

        return self.process_batch(selected, output_dir=processed_dir, skip_existing=True)

    def optimize_for_video(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        target_width: int = 1920,
        target_height: int = 1080
    ) -> Path:
        """
        Optimize processed image for video compositing

        Args:
            input_path: Path to transparent PNG
            output_path: Output path (overwrites input if None)
            target_width: Target video width
            target_height: Target video height

        Returns:
            Path to optimized image
        """
        input_path = Path(input_path)
        output_path = Path(output_path) if output_path else input_path

        with Image.open(input_path) as img:
            # Ensure RGBA for transparency
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            # Calculate scaling to fit within video frame (with padding)
            max_width = int(target_width * 0.7)  # 70% of frame width
            max_height = int(target_height * 0.7)

            # Maintain aspect ratio
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            # Save optimized
            img.save(output_path, format="PNG", optimize=True)
            logger.info(f"Optimized for video: {output_path.name} ({img.size[0]}x{img.size[1]})")

        return output_path

    def _get_mime_type(self, path: Path) -> str:
        """Get MIME type for image file"""
        ext = path.suffix.lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
            ".gif": "image/gif"
        }
        return mime_types.get(ext, "image/jpeg")

    def get_api_usage(self) -> dict:
        """Get current API usage/credits (if supported by Removal.AI)"""
        try:
            headers = {"Rm-Token": self.api_key}
            response = requests.get(
                "https://api.removal.ai/3.0/account",
                headers=headers,
                timeout=10
            )
            if response.ok:
                return response.json()
            return {"status": "unable to fetch"}
        except Exception as e:
            return {"error": str(e)}


# Example usage and testing
if __name__ == "__main__":
    import sys
    
    # Test with command line argument or default
    if len(sys.argv) > 1:
        test_image = Path(sys.argv[1])
    else:
        # Default test: first listing image
        test_image = Path("assets/4802/156359BB/photo_01.jpg")

    if not test_image.exists():
        print(f"Test image not found: {test_image}")
        print("Usage: python image_processor.py <image_path>")
        sys.exit(1)

    # Initialize processor
    processor = ImageProcessor(output_format=OutputFormat.PNG)

    # Process single image
    print(f"\n🖼️  Processing: {test_image}")
    print("-" * 50)
    
    result = processor.remove_background(test_image)
    
    if result.success:
        print(f"✓ Success!")
        print(f"  Input:  {result.input_path}")
        print(f"  Output: {result.output_path}")
        print(f"  Size:   {result.file_size_kb:.1f} KB")
    else:
        print(f"✗ Failed: {result.error}")

