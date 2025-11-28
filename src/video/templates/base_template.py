"""
Base template for video composition
All templates inherit from this class
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import logging

try:
    from moviepy.editor import (
        VideoClip, ImageClip, TextClip, CompositeVideoClip,
        ColorClip, concatenate_videoclips
    )
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseTemplate(ABC):
    """Base class for all video templates"""
    
    def __init__(
        self,
        resolution: Tuple[int, int] = (1920, 1080),
        fps: int = 30,
        duration: float = 30.0
    ):
        """
        Initialize base template
        
        Args:
            resolution: Video resolution (width, height)
            fps: Frames per second
            duration: Total video duration in seconds
        """
        if not MOVIEPY_AVAILABLE:
            raise ImportError("MoviePy not available. Run: pip install moviepy")
        
        self.resolution = resolution
        self.width, self.height = resolution
        self.fps = fps
        self.duration = duration
        
        # Timeline structure (in seconds)
        self.timeline = {
            'intro': (0, 3),           # Brand intro
            'reveal': (3, 8),          # Bike reveal
            'features': (8, 15),       # Feature highlights
            'price': (15, 22),         # Price slash
            'cta': (22, 27),           # CTA with QR
            'outro': (27, 30)          # Dealer logo
        }
        
        logger.info(f"Initialized {self.__class__.__name__} template ({resolution[0]}x{resolution[1]} @ {fps}fps)")
    
    @abstractmethod
    def get_background(self) -> VideoClip:
        """
        Create background layer
        
        Returns:
            VideoClip with background
        """
        pass
    
    @abstractmethod
    def create_intro(self, brand_logo: Optional[str] = None) -> VideoClip:
        """
        Create brand intro segment (0-3s)
        
        Args:
            brand_logo: Path to brand logo image
            
        Returns:
            VideoClip for intro
        """
        pass
    
    @abstractmethod
    def create_bike_reveal(
        self,
        bike_image: str,
        bike_data: Dict[str, Any]
    ) -> VideoClip:
        """
        Create bike reveal segment (3-8s)
        
        Args:
            bike_image: Path to processed bike image
            bike_data: Dictionary with bike information
            
        Returns:
            VideoClip for bike reveal
        """
        pass
    
    @abstractmethod
    def create_features(
        self,
        bike_data: Dict[str, Any]
    ) -> VideoClip:
        """
        Create features segment (8-15s)
        
        Args:
            bike_data: Dictionary with bike information
            
        Returns:
            VideoClip for features
        """
        pass
    
    @abstractmethod
    def create_price_reveal(
        self,
        price: float,
        msrp: Optional[float] = None
    ) -> VideoClip:
        """
        Create price reveal segment (15-22s)
        
        Args:
            price: Listing price
            msrp: MSRP for savings calculation
            
        Returns:
            VideoClip for price reveal
        """
        pass
    
    @abstractmethod
    def create_cta(
        self,
        qr_code: str,
        dealer_name: str
    ) -> VideoClip:
        """
        Create CTA segment (22-27s)
        
        Args:
            qr_code: Path to QR code image
            dealer_name: Dealer name
            
        Returns:
            VideoClip for CTA
        """
        pass
    
    @abstractmethod
    def create_outro(
        self,
        dealer_logo: Optional[str] = None
    ) -> VideoClip:
        """
        Create outro segment (27-30s)
        
        Args:
            dealer_logo: Path to dealer logo
            
        Returns:
            VideoClip for outro
        """
        pass
    
    def get_text_style(self, style_type: str = "default") -> Dict[str, Any]:
        """
        Get text styling parameters
        
        Args:
            style_type: Type of text style (title, subtitle, body, etc.)
            
        Returns:
            Dictionary with text styling parameters
        """
        styles = {
            'title': {
                'fontsize': 120,
                'color': 'white',
                'font': 'Impact',
                'stroke_color': 'black',
                'stroke_width': 3
            },
            'subtitle': {
                'fontsize': 80,
                'color': 'white',
                'font': 'Arial-Bold',
                'stroke_color': 'black',
                'stroke_width': 2
            },
            'body': {
                'fontsize': 60,
                'color': 'white',
                'font': 'Arial',
                'stroke_color': 'black',
                'stroke_width': 1
            },
            'price': {
                'fontsize': 150,
                'color': 'red',
                'font': 'Impact',
                'stroke_color': 'white',
                'stroke_width': 4
            },
            'cta': {
                'fontsize': 90,
                'color': 'yellow',
                'font': 'Impact',
                'stroke_color': 'black',
                'stroke_width': 3
            }
        }
        
        return styles.get(style_type, styles['body'])
    
    def compose_segments(self, segments: list) -> VideoClip:
        """
        Compose multiple segments into final video
        
        Args:
            segments: List of VideoClip segments
            
        Returns:
            Composite video clip
        """
        try:
            # Concatenate all segments
            final = concatenate_videoclips(segments, method="compose")
            
            # Ensure exact duration
            if final.duration != self.duration:
                final = final.set_duration(self.duration)
            
            return final
        
        except Exception as e:
            logger.error(f"Failed to compose segments: {e}")
            raise
    
    def create_video(
        self,
        bike_data: Dict[str, Any],
        bike_image: str,
        qr_code: str,
        brand_logo: Optional[str] = None,
        dealer_logo: Optional[str] = None,
        dealer_name: str = "San Diego Harley-Davidson"
    ) -> VideoClip:
        """
        Create complete video from all segments
        
        Args:
            bike_data: Dictionary with bike information
            bike_image: Path to processed bike image
            qr_code: Path to QR code
            brand_logo: Path to brand logo (optional)
            dealer_logo: Path to dealer logo (optional)
            dealer_name: Dealer name
            
        Returns:
            Complete VideoClip
        """
        logger.info("Creating video segments...")
        
        # Create all segments
        segments = []
        
        # Background (full duration)
        background = self.get_background()
        
        # Intro (0-3s)
        intro = self.create_intro(brand_logo)
        segments.append(intro)
        
        # Bike reveal (3-8s)
        reveal = self.create_bike_reveal(bike_image, bike_data)
        segments.append(reveal)
        
        # Features (8-15s)
        features = self.create_features(bike_data)
        segments.append(features)
        
        # Price reveal (15-22s)
        price = self.create_price_reveal(
            bike_data.get('price', 0),
            bike_data.get('msrp')
        )
        segments.append(price)
        
        # CTA (22-27s)
        cta = self.create_cta(qr_code, dealer_name)
        segments.append(cta)
        
        # Outro (27-30s)
        outro = self.create_outro(dealer_logo)
        segments.append(outro)
        
        # Compose final video
        logger.info("Composing final video...")
        final = self.compose_segments(segments)
        
        # Add background
        final = CompositeVideoClip([background, final])
        
        return final


# Template utilities
def create_fade_in(clip: VideoClip, duration: float = 0.5) -> VideoClip:
    """Add fade in effect to clip"""
    return clip.fadein(duration)


def create_fade_out(clip: VideoClip, duration: float = 0.5) -> VideoClip:
    """Add fade out effect to clip"""
    return clip.fadeout(duration)


def create_zoom_effect(
    clip: VideoClip,
    start_scale: float = 0.8,
    end_scale: float = 1.0,
    duration: Optional[float] = None
) -> VideoClip:
    """Add zoom effect to clip"""
    if duration is None:
        duration = clip.duration
    
    def zoom(t):
        scale = start_scale + (end_scale - start_scale) * (t / duration)
        return clip.resize(scale)
    
    return clip.fl(zoom, apply_to=['mask'])


def create_slide_in(
    clip: VideoClip,
    direction: str = "left",
    duration: Optional[float] = None
) -> VideoClip:
    """Add slide in effect"""
    if duration is None:
        duration = clip.duration
    
    w, h = clip.size
    
    positions = {
        'left': lambda t: (int(-w + (w * 1.5) * (t / duration)), 'center'),
        'right': lambda t: (int(w * 2 - (w * 1.5) * (t / duration)), 'center'),
        'top': lambda t: ('center', int(-h + (h * 1.5) * (t / duration))),
        'bottom': lambda t: ('center', int(h * 2 - (h * 1.5) * (t / duration)))
    }
    
    return clip.set_position(positions.get(direction, positions['left']))



