"""
Simplified Dark Template - Works without ImageMagick
Uses PIL for all text rendering
"""

from typing import Dict, Any, Optional
from pathlib import Path
import logging
import numpy as np

try:
    from moviepy.editor import (
        VideoClip, ImageClip, CompositeVideoClip,
        ColorClip, concatenate_videoclips
    )
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

from .base_template import BaseTemplate
from ..text_utils import create_text_image, create_multiline_text_image

logger = logging.getLogger(__name__)


class SimpleDarkTemplate(BaseTemplate):
    """Simplified dark template using PIL for text (no ImageMagick)"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Colors
        self.bg_color = (26, 26, 26)  # Dark gray
        self.accent_color = (255, 0, 0)  # Red
    
    def get_background(self) -> VideoClip:
        """Dark background"""
        return ColorClip(
            size=self.resolution,
            color=self.bg_color,
            duration=self.duration
        )
    
    def create_intro(self, brand_logo: Optional[str] = None) -> VideoClip:
        """Brand intro (0-3s)"""
        start, end = self.timeline['intro']
        duration = end - start
        
        # Create title image with PIL
        title_img = create_text_image(
            "SLASHER SALE",
            size=self.resolution,
            font_size=150,
            color=(255, 0, 0),  # Red
            stroke_color=(255, 255, 255),  # White outline
            stroke_width=5
        )
        
        # Create subtitle at a specific position
        subtitle_size = (self.width, 150)
        subtitle_img = create_text_image(
            "24/7 HARLEY-DAVIDSON DEALS",
            size=subtitle_size,
            font_size=60,
            color=(255, 255, 255)
        )
        
        # Create full-size image for subtitle
        subtitle_positioned = np.zeros((self.height, self.width, 4), dtype=np.uint8)
        y_pos = int(self.height * 0.6)
        subtitle_positioned[y_pos:y_pos+subtitle_size[1], :, :] = subtitle_img
        
        # Create clips
        title_clip = ImageClip(title_img).set_duration(duration)
        subtitle_clip = ImageClip(subtitle_positioned).set_duration(duration)
        
        # Fade in
        title_clip = title_clip.fadein(0.5)
        subtitle_clip = subtitle_clip.fadein(1.0)
        
        # Compose
        return CompositeVideoClip([title_clip, subtitle_clip], size=self.resolution).set_start(start)
    
    def create_bike_reveal(self, bike_image: str, bike_data: Dict[str, Any]) -> VideoClip:
        """Bike reveal (3-8s)"""
        start, end = self.timeline['reveal']
        duration = end - start
        
        # Load bike image
        bike_clip = ImageClip(bike_image).set_duration(duration)
        bike_clip = bike_clip.resize(height=int(self.height * 0.7))
        bike_clip = bike_clip.set_position('center')
        
        # Bike name text
        bike_name = f"{bike_data.get('year')} {bike_data.get('make')} {bike_data.get('model', '')}"
        title_img = create_text_image(
            bike_name[:40],  # Limit length
            size=(self.width, 150),
            font_size=80,
            color=(255, 255, 255),
            stroke_color=(0, 0, 0),
            stroke_width=3
        )
        
        title_clip = ImageClip(title_img).set_duration(duration)
        title_clip = title_clip.set_position(('center', 50))
        title_clip = title_clip.fadein(0.5)
        
        # Fade in bike
        bike_clip = bike_clip.fadein(0.5)
        
        return CompositeVideoClip([bike_clip, title_clip], size=self.resolution).set_start(start)
    
    def create_features(self, bike_data: Dict[str, Any]) -> VideoClip:
        """Features (8-15s)"""
        start, end = self.timeline['features']
        duration = end - start
        
        # Collect features
        features = []
        if bike_data.get('engine_displacement'):
            features.append(f"ENGINE: {bike_data['engine_displacement']}")
        if bike_data.get('odometer'):
            features.append(f"MILES: {bike_data['odometer']:,}")
        if bike_data.get('color'):
            features.append(f"COLOR: {bike_data['color']}")
        
        # Create feature text
        feature_text = "\n".join(features[:3])  # Max 3 features
        
        if feature_text:
            text_img = create_multiline_text_image(
                feature_text,
                size=self.resolution,
                font_size=70,
                color=(255, 255, 255),
                stroke_color=(255, 0, 0),
                stroke_width=2
            )
            
            clip = ImageClip(text_img).set_duration(duration)
            clip = clip.fadein(0.5)
            return clip.set_start(start)
        else:
            # Empty clip
            return ColorClip(self.resolution, color=(0,0,0,0)).set_duration(duration).set_start(start)
    
    def create_price_reveal(self, price: float, msrp: Optional[float] = None) -> VideoClip:
        """Price reveal (15-22s)"""
        start, end = self.timeline['price']
        duration = end - start
        
        # Price text
        price_str = f"${price:,.0f}"
        price_img = create_text_image(
            price_str,
            size=self.resolution,
            font_size=180,
            color=(255, 0, 0),  # Red
            stroke_color=(255, 255, 255),
            stroke_width=6
        )
        
        # Label
        label_img = create_text_image(
            "NOW ONLY",
            size=(self.width, 150),
            font_size=70,
            color=(255, 255, 0),  # Yellow
            stroke_color=(0, 0, 0),
            stroke_width=3
        )
        
        # Position label at top
        label_positioned = np.zeros((self.height, self.width, 4), dtype=np.uint8)
        label_positioned[:150, :, :] = label_img[:150, :, :]
        
        price_clip = ImageClip(price_img).set_duration(duration)
        label_clip = ImageClip(label_positioned).set_duration(duration)
        
        price_clip = price_clip.fadein(0.8)
        label_clip = label_clip.fadein(0.5)
        
        return CompositeVideoClip([label_clip, price_clip], size=self.resolution).set_start(start)
    
    def create_cta(self, qr_code: str, dealer_name: str) -> VideoClip:
        """CTA (22-27s)"""
        start, end = self.timeline['cta']
        duration = end - start
        
        # QR code - ensure it's RGBA format
        from PIL import Image
        qr_img = Image.open(qr_code)
        if qr_img.mode != 'RGBA':
            qr_img = qr_img.convert('RGBA')
        qr_array = np.array(qr_img)
        
        qr_clip = ImageClip(qr_array).set_duration(duration)
        qr_clip = qr_clip.resize(height=int(self.height * 0.5))
        qr_clip = qr_clip.set_position('center')
        qr_clip = qr_clip.fadein(0.5)
        
        # CTA text
        cta_img = create_text_image(
            "SCAN TO RESERVE NOW",
            size=(self.width, 150),
            font_size=90,
            color=(255, 255, 0),
            stroke_color=(0, 0, 0),
            stroke_width=4
        )
        
        # Position at top
        cta_positioned = np.zeros((self.height, self.width, 4), dtype=np.uint8)
        cta_positioned[:150, :, :] = cta_img[:150, :, :]
        
        cta_clip = ImageClip(cta_positioned).set_duration(duration)
        cta_clip = cta_clip.fadein(0.5)
        
        return CompositeVideoClip([qr_clip, cta_clip], size=self.resolution).set_start(start)
    
    def create_outro(self, dealer_logo: Optional[str] = None) -> VideoClip:
        """Outro (27-30s)"""
        start, end = self.timeline['outro']
        duration = end - start
        
        # Message
        message_img = create_multiline_text_image(
            "DON'T WAIT!\nRIDE TODAY!",
            size=self.resolution,
            font_size=90,
            color=(255, 0, 0),
            stroke_color=(255, 255, 255),
            stroke_width=3
        )
        
        message_clip = ImageClip(message_img).set_duration(duration)
        message_clip = message_clip.fadein(0.5).fadeout(0.5)
        
        return message_clip.set_start(start)


# Update imports to use this simplified version
DarkTemplate = SimpleDarkTemplate


__all__ = ['DarkTemplate', 'SimpleDarkTemplate']

