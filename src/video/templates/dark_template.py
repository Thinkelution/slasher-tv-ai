"""
Dark Template - Aggressive, dramatic motorcycle video style
Perfect for sport bikes and high-performance models
"""

from typing import Dict, Any, Optional
from pathlib import Path
import logging

try:
    from moviepy.editor import (
        VideoClip, ImageClip, CompositeVideoClip,
        ColorClip, concatenate_videoclips
    )
    from moviepy.video.fx import resize, fadein, fadeout
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

from .base_template import BaseTemplate, create_fade_in, create_fade_out
from ..text_utils import create_text_image, create_multiline_text_image
import numpy as np

logger = logging.getLogger(__name__)


class DarkTemplate(BaseTemplate):
    """Dark, aggressive template for motorcycle videos"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Dark theme colors
        self.bg_color = (26, 26, 26)  # Dark gray
        self.accent_color = (255, 0, 0)  # Red
        self.text_color = (255, 255, 255)  # White
    
    def get_background(self) -> VideoClip:
        """Create dark background"""
        return ColorClip(
            size=self.resolution,
            color=self.bg_color,
            duration=self.duration
        )
    
    def create_intro(self, brand_logo: Optional[str] = None) -> VideoClip:
        """
        Create brand intro (0-3s)
        SLASHER SALE logo animation
        """
        start, end = self.timeline['intro']
        duration = end - start
        
        # Main title
        title = TextClip(
            "SLASHER SALE",
            fontsize=150,
            color='red',
            font='Impact',
            stroke_color='white',
            stroke_width=5
        ).set_duration(duration).set_position('center')
        
        # Subtitle
        subtitle = TextClip(
            "24/7 HARLEY-DAVIDSON DEALS",
            fontsize=60,
            color='white',
            font='Arial-Bold'
        ).set_duration(duration).set_position(('center', self.height * 0.6))
        
        # Add fade effects
        title = create_fade_in(title, 0.5)
        subtitle = create_fade_in(subtitle, 1.0)
        
        # Compose
        clip = CompositeVideoClip([title, subtitle], size=self.resolution)
        return clip.set_start(start).set_duration(duration)
    
    def create_bike_reveal(
        self,
        bike_image: str,
        bike_data: Dict[str, Any]
    ) -> VideoClip:
        """
        Create bike reveal (3-8s)
        Hero image with bike name
        """
        start, end = self.timeline['reveal']
        duration = end - start
        
        # Load bike image
        bike_clip = ImageClip(bike_image).set_duration(duration)
        
        # Resize to fit (maintain aspect ratio)
        bike_clip = bike_clip.resize(height=self.height * 0.7)
        bike_clip = bike_clip.set_position('center')
        
        # Add zoom effect (0.8x to 1.0x)
        def zoom_effect(t):
            progress = t / duration
            scale = 0.8 + (0.2 * progress)
            return scale
        
        bike_clip = bike_clip.resize(lambda t: zoom_effect(t))
        
        # Bike name text
        bike_name = f"{bike_data.get('year')} {bike_data.get('make')} {bike_data.get('model', '')}"
        title = TextClip(
            bike_name,
            fontsize=100,
            color='white',
            font='Impact',
            stroke_color='black',
            stroke_width=3
        ).set_duration(duration).set_position(('center', self.height * 0.1))
        
        # Add fade
        title = create_fade_in(title, 0.5)
        bike_clip = create_fade_in(bike_clip, 0.5)
        
        # Compose
        clip = CompositeVideoClip([bike_clip, title], size=self.resolution)
        return clip.set_start(start).set_duration(duration)
    
    def create_features(
        self,
        bike_data: Dict[str, Any]
    ) -> VideoClip:
        """
        Create features segment (8-15s)
        Display key specs
        """
        start, end = self.timeline['features']
        duration = end - start
        
        # Collect features
        features = []
        
        if bike_data.get('engine_displacement'):
            features.append(f"ENGINE: {bike_data['engine_displacement']}")
        
        if bike_data.get('odometer'):
            mileage = bike_data['odometer']
            if mileage < 5000:
                features.append(f"LOW MILES: {mileage:,}")
            else:
                features.append(f"MILES: {mileage:,}")
        
        if bike_data.get('color'):
            features.append(f"COLOR: {bike_data['color']}")
        
        if bike_data.get('condition'):
            features.append(f"{bike_data['condition'].upper()}")
        
        # Create text clips
        y_positions = [0.3, 0.45, 0.6, 0.75]
        clips = []
        
        for i, feature in enumerate(features[:4]):  # Max 4 features
            y_pos = y_positions[i]
            
            text = TextClip(
                feature,
                fontsize=80,
                color='white',
                font='Impact',
                stroke_color='red',
                stroke_width=2
            ).set_duration(duration).set_position(('center', self.height * y_pos))
            
            # Stagger fade-in
            text = text.set_start(i * 0.3)
            text = create_fade_in(text, 0.5)
            
            clips.append(text)
        
        # Compose
        clip = CompositeVideoClip(clips, size=self.resolution)
        return clip.set_start(start).set_duration(duration)
    
    def create_price_reveal(
        self,
        price: float,
        msrp: Optional[float] = None
    ) -> VideoClip:
        """
        Create price reveal (15-22s)
        Dramatic price slash effect
        """
        start, end = self.timeline['price']
        duration = end - start
        
        # Format price
        price_str = f"${price:,.0f}"
        
        # Price text
        price_clip = TextClip(
            price_str,
            fontsize=180,
            color='red',
            font='Impact',
            stroke_color='white',
            stroke_width=6
        ).set_duration(duration).set_position('center')
        
        # "NOW ONLY" text
        label = TextClip(
            "NOW ONLY",
            fontsize=70,
            color='yellow',
            font='Impact',
            stroke_color='black',
            stroke_width=3
        ).set_duration(duration).set_position(('center', self.height * 0.3))
        
        # Savings text if MSRP available
        clips = [label, price_clip]
        
        if msrp and msrp > price:
            savings = msrp - price
            savings_text = TextClip(
                f"SAVE ${savings:,.0f}!",
                fontsize=60,
                color='lime',
                font='Impact',
                stroke_color='black',
                stroke_width=2
            ).set_duration(duration).set_position(('center', self.height * 0.7))
            clips.append(savings_text)
        
        # Add dramatic fade effects
        for clip in clips:
            clip = create_fade_in(clip, 0.8)
        
        # Compose
        final = CompositeVideoClip(clips, size=self.resolution)
        return final.set_start(start).set_duration(duration)
    
    def create_cta(
        self,
        qr_code: str,
        dealer_name: str
    ) -> VideoClip:
        """
        Create CTA segment (22-27s)
        QR code + call to action
        """
        start, end = self.timeline['cta']
        duration = end - start
        
        # QR code
        qr_clip = ImageClip(qr_code).set_duration(duration)
        qr_clip = qr_clip.resize(height=self.height * 0.5)
        qr_clip = qr_clip.set_position('center')
        
        # CTA text
        cta_text = TextClip(
            "SCAN TO RESERVE NOW",
            fontsize=100,
            color='yellow',
            font='Impact',
            stroke_color='black',
            stroke_width=4
        ).set_duration(duration).set_position(('center', self.height * 0.15))
        
        # Dealer text
        dealer_text = TextClip(
            f"AVAILABLE AT {dealer_name.upper()}",
            fontsize=50,
            color='white',
            font='Arial-Bold'
        ).set_duration(duration).set_position(('center', self.height * 0.85))
        
        # Add pulse effect to CTA
        def pulse(t):
            # Pulse between 0.95 and 1.05
            scale = 1.0 + 0.05 * abs(t % 1.0 - 0.5) * 4
            return scale
        
        cta_text = cta_text.resize(lambda t: pulse(t))
        
        # Fade in
        qr_clip = create_fade_in(qr_clip, 0.5)
        cta_text = create_fade_in(cta_text, 0.5)
        dealer_text = create_fade_in(dealer_text, 0.8)
        
        # Compose
        clip = CompositeVideoClip([qr_clip, cta_text, dealer_text], size=self.resolution)
        return clip.set_start(start).set_duration(duration)
    
    def create_outro(
        self,
        dealer_logo: Optional[str] = None
    ) -> VideoClip:
        """
        Create outro segment (27-30s)
        Dealer logo + final message
        """
        start, end = self.timeline['outro']
        duration = end - start
        
        # Final message
        message = TextClip(
            "DON'T WAIT!\nRIDE TODAY!",
            fontsize=90,
            color='red',
            font='Impact',
            stroke_color='white',
            stroke_width=3,
            method='caption',
            align='center',
            size=(self.width * 0.8, None)
        ).set_duration(duration).set_position('center')
        
        # Website
        website = TextClip(
            "SLASHERSALE.TV",
            fontsize=60,
            color='white',
            font='Arial-Bold'
        ).set_duration(duration).set_position(('center', self.height * 0.75))
        
        # Fade effects
        message = create_fade_in(message, 0.5)
        message = create_fade_out(message, 0.5)
        website = create_fade_in(website, 0.8)
        
        # Compose
        clip = CompositeVideoClip([message, website], size=self.resolution)
        return clip.set_start(start).set_duration(duration)


# Export
__all__ = ['DarkTemplate']

