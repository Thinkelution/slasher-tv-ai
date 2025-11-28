"""
Motorcycle Image Processor v2.5 - Remove.bg API + Fallback
Uses Remove.bg API for professional background removal
Falls back to rembg if API unavailable
"""

import io
import os
import logging
import requests
from pathlib import Path
from typing import Tuple, Optional
from dotenv import load_dotenv

load_dotenv()

try:
    from PIL import Image, ImageEnhance, ImageFilter
    import numpy as np
    import cv2
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from rembg import remove, new_session
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger(__name__)


class MotorcycleExtractor:
    """
    Professional motorcycle extraction using Remove.bg API
    Falls back to rembg if API is unavailable
    """
    
    # Remove.bg API endpoint
    REMOVEBG_API_URL = "https://api.remove.bg/v1.0/removebg"
    
    def __init__(self, api_key: Optional[str] = None, use_api: bool = True):
        """
        Initialize extractor
        
        Args:
            api_key: Remove.bg API key (or set REMOVEBG_API_KEY env var)
            use_api: Whether to use Remove.bg API (True) or rembg (False)
        """
        if not PIL_AVAILABLE:
            raise ImportError("pip install Pillow numpy opencv-python")
        
        self.api_key = api_key or os.getenv("REMOVEBG_API_KEY")
        self.use_api = use_api and self.api_key is not None
        
        # Initialize rembg as fallback
        self.rembg_session = None
        if REMBG_AVAILABLE:
            try:
                self.rembg_session = new_session("isnet-general-use")
                log.info("rembg fallback ready")
            except:
                pass
        
        if self.use_api:
            log.info("Using Remove.bg API for background removal")
        elif self.rembg_session:
            log.info("Using rembg (local) for background removal")
        else:
            log.warning("No background removal method available!")
    
    # ==================== REMOVE.BG API ====================
    
    def extract_with_api(self, image: Image.Image) -> Optional[Image.Image]:
        """
        Remove background using Remove.bg API
        
        Args:
            image: PIL Image
            
        Returns:
            Image with transparent background or None if failed
        """
        if not self.api_key:
            log.warning("No Remove.bg API key provided")
            return None
        
        try:
            # Convert image to bytes
            buf = io.BytesIO()
            image.save(buf, format='PNG')
            buf.seek(0)
            
            # Send to API
            headers = {
                "X-Api-Key": self.api_key
            }
            
            files = {
                "image_file": ("image.png", buf, "image/png")
            }
            
            data = {
                "size": "auto",
                "format": "png",
                "type": "product"  # Good for vehicles/products
            }
            
            log.info("  Sending to Remove.bg API...")
            response = requests.post(
                self.REMOVEBG_API_URL,
                headers=headers,
                files=files,
                data=data,
                timeout=60
            )
            
            if response.status_code == 200:
                # Success - return the result
                result = Image.open(io.BytesIO(response.content)).convert('RGBA')
                credits = response.headers.get('X-Credits-Remaining', 'unknown')
                log.info(f"  API extraction successful (credits remaining: {credits})")
                return result
            elif response.status_code == 402:
                log.warning("  API credits exhausted - falling back to local processing")
                return None
            elif response.status_code == 429:
                log.warning("  API rate limited - falling back to local processing")
                return None
            else:
                log.warning(f"  API error {response.status_code}: {response.text[:100]}")
                return None
                
        except requests.exceptions.Timeout:
            log.warning("  API timeout - falling back to local processing")
            return None
        except Exception as e:
            log.warning(f"  API error: {e}")
            return None
    
    # ==================== REMBG FALLBACK ====================
    
    def extract_with_rembg(self, image: Image.Image) -> Optional[Image.Image]:
        """
        Remove background using rembg (local)
        
        Args:
            image: PIL Image
            
        Returns:
            Image with transparent background
        """
        if not REMBG_AVAILABLE or not self.rembg_session:
            log.warning("rembg not available")
            return None
        
        try:
            buf = io.BytesIO()
            image.save(buf, format='PNG')
            
            result = remove(
                buf.getvalue(),
                session=self.rembg_session,
                alpha_matting=False,
                post_process_mask=False
            )
            
            return Image.open(io.BytesIO(result)).convert('RGBA')
            
        except Exception as e:
            log.error(f"rembg error: {e}")
            return None
    
    # ==================== MAIN EXTRACTION ====================
    
    def extract(self, image: Image.Image) -> Image.Image:
        """
        Extract subject from background
        Tries Remove.bg API first, falls back to rembg
        
        Args:
            image: PIL Image
            
        Returns:
            Image with transparent background
        """
        result = None
        
        # Try API first
        if self.use_api:
            result = self.extract_with_api(image)
        
        # Fallback to rembg
        if result is None and self.rembg_session:
            log.info("  Using rembg fallback...")
            result = self.extract_with_rembg(image)
        
        # If still none, return original with alpha
        if result is None:
            log.warning("  No extraction method worked, returning original")
            result = image.convert('RGBA')
        
        return result
    
    # ==================== POST-PROCESSING ====================
    
    def clean_edges(self, image: Image.Image) -> Image.Image:
        """Clean up edges and remove artifacts"""
        if image.mode != 'RGBA':
            return image
        
        arr = np.array(image)
        alpha = arr[:, :, 3]
        
        # Simple threshold - clean alpha
        arr[:, :, 3] = np.where(alpha > 128, 255, 0).astype(np.uint8)
        
        return Image.fromarray(arr)
    
    def remove_halo(self, image: Image.Image) -> Image.Image:
        """Remove white/light halo around edges"""
        if image.mode != 'RGBA':
            return image
        
        arr = np.array(image)
        r, g, b, a = arr[:,:,0], arr[:,:,1], arr[:,:,2], arr[:,:,3]
        
        # Find semi-transparent light pixels
        semi = (a > 10) & (a < 240)
        brightness = (r.astype(int) + g.astype(int) + b.astype(int)) / 3
        light_halo = semi & (brightness > 200)
        
        arr[:,:,3] = np.where(light_halo, 0, arr[:,:,3])
        
        return Image.fromarray(arr)
    
    def crop_to_content(self, image: Image.Image, padding: int = 15) -> Image.Image:
        """Crop to content bounds"""
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        alpha = np.array(image.split()[3])
        visible = alpha > 30
        
        if not np.any(visible):
            return image
        
        rows = np.any(visible, axis=1)
        cols = np.any(visible, axis=0)
        y1, y2 = np.where(rows)[0][[0, -1]]
        x1, x2 = np.where(cols)[0][[0, -1]]
        
        y1 = max(0, y1 - padding)
        y2 = min(image.height, y2 + padding)
        x1 = max(0, x1 - padding)
        x2 = min(image.width, x2 + padding)
        
        return image.crop((x1, y1, x2, y2))
    
    def enhance(self, image: Image.Image) -> Image.Image:
        """Enhance image quality"""
        if image.mode != 'RGBA':
            return image
        
        r, g, b, a = image.split()
        rgb = Image.merge('RGB', (r, g, b))
        
        rgb = rgb.filter(ImageFilter.UnsharpMask(radius=1, percent=100, threshold=2))
        rgb = ImageEnhance.Contrast(rgb).enhance(1.05)
        
        result = rgb.convert('RGBA')
        result.putalpha(a)
        return result
    
    def analyze_quality(self, image: Image.Image) -> dict:
        """Analyze extraction quality"""
        if image.mode != 'RGBA':
            return {'valid': False}
        
        alpha = np.array(image.split()[3])
        total = alpha.size
        solid = np.sum(alpha == 255)
        transparent = np.sum(alpha == 0)
        semi = total - solid - transparent
        
        semi_ratio = semi / total
        
        return {
            'valid': True,
            'semi_ratio': semi_ratio,
            'quality': 'EXCELLENT' if semi_ratio < 0.01 else 'GOOD' if semi_ratio < 0.05 else 'FAIR'
        }
    
    # ==================== MAIN PIPELINE ====================
    
    def process(self, input_path: str, output_path: str) -> Tuple[bool, dict]:
        """
        Complete processing pipeline
        
        Args:
            input_path: Input image path
            output_path: Output PNG path
            
        Returns:
            (success, quality_info)
        """
        name = Path(input_path).name
        log.info(f"\n{'='*50}")
        log.info(f"Processing: {name}")
        
        try:
            # Load image
            original = Image.open(input_path).convert('RGB')
            log.info(f"  Input: {original.size}")
            
            # Step 1: Extract background
            log.info("  [1] Extracting background...")
            img = self.extract(original)
            
            # Step 2: Remove halo
            log.info("  [2] Removing halo...")
            img = self.remove_halo(img)
            
            # Step 3: Clean edges
            log.info("  [3] Cleaning edges...")
            img = self.clean_edges(img)
            
            # Step 4: Enhance
            log.info("  [4] Enhancing...")
            img = self.enhance(img)
            
            # Step 5: Crop
            log.info("  [5] Cropping...")
            img = self.crop_to_content(img)
            
            # Step 6: Resize if needed
            max_dim = 1920
            if img.width > max_dim or img.height > max_dim:
                ratio = min(max_dim / img.width, max_dim / img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Analyze quality
            quality = self.analyze_quality(img)
            log.info(f"  Quality: {quality['quality']} (semi: {quality['semi_ratio']:.3f})")
            
            # Save
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            img.save(output_path, 'PNG', optimize=True)
            
            log.info(f"  [OK] {img.size[0]}x{img.size[1]}")
            return True, quality
            
        except Exception as e:
            log.error(f"  [FAIL] {e}")
            return False, {'valid': False, 'error': str(e)}
    
    def process_batch(
        self,
        input_dir: str,
        output_dir: str,
        pattern: str = "photo_*.jpg"
    ) -> dict:
        """Process all images in directory"""
        in_path = Path(input_dir)
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        
        # Find images
        images = sorted(in_path.glob(pattern))
        if not images:
            for ext in ['.jpg', '.jpeg', '.png', '.JPG']:
                images.extend(in_path.glob(f"*{ext}"))
            images = sorted(set(images))
        
        log.info(f"\nFound {len(images)} images")
        
        stats = {
            'total': len(images),
            'success': 0,
            'excellent': 0,
            'good': 0,
            'fair': 0,
            'failed': []
        }
        
        for i, img_path in enumerate(images):
            out_file = out_path / f"bike_{i:02d}.png"
            try:
                ok, quality = self.process(str(img_path), str(out_file))
                if ok:
                    stats['success'] += 1
                    q = quality.get('quality', 'FAIR').lower()
                    stats[q] = stats.get(q, 0) + 1
            except Exception as e:
                log.error(f"  [FAIL] {e}")
                stats['failed'].append(str(e))
        
        log.info(f"\n{'='*50}")
        log.info("RESULTS:")
        log.info(f"  Success: {stats['success']}/{stats['total']}")
        log.info(f"  Excellent: {stats['excellent']}")
        log.info(f"  Good: {stats['good']}")
        
        return stats


# Alias for compatibility
ImageProcessor = MotorcycleExtractor


def main():
    """Run processor"""
    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent.parent
    os.chdir(project_root)
    
    log.info("="*60)
    log.info("Motorcycle Extractor v2.5")
    log.info("Remove.bg API + rembg fallback")
    log.info("="*60)
    
    input_dir = Path("assets/4802/156359BB")
    if not input_dir.exists():
        log.error(f"Not found: {input_dir}")
        return
    
    images = list(input_dir.glob("photo_*.jpg"))
    log.info(f"Found {len(images)} images")
    
    if not images:
        return
    
    # Check for API key
    api_key = os.getenv("REMOVEBG_API_KEY")
    if api_key:
        log.info("Remove.bg API key found - using API")
    else:
        log.info("No API key - using rembg local processing")
    
    extractor = MotorcycleExtractor(api_key=api_key)
    
    stats = extractor.process_batch(
        str(input_dir),
        str(input_dir / "v2_output"),
        "photo_*.jpg"
    )
    
    log.info(f"\nOutput: {input_dir / 'v2_output'}")


if __name__ == "__main__":
    main()
