"""
Text rendering utilities using PIL (no ImageMagick required)
"""

from PIL import Image, ImageDraw, ImageFont
import numpy as np
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def create_text_image(
    text: str,
    size: Tuple[int, int],
    font_size: int = 100,
    color: Tuple[int, int, int] = (255, 255, 255),
    bg_color: Optional[Tuple[int, int, int, int]] = None,
    stroke_color: Optional[Tuple[int, int, int]] = None,
    stroke_width: int = 0,
    font_name: str = "arial.ttf",
    align: str = "center"
) -> np.ndarray:
    """
    Create text image using PIL
    
    Args:
        text: Text to render
        size: Image size (width, height)
        font_size: Font size
        color: Text color RGB
        bg_color: Background color RGBA (None for transparent)
        stroke_color: Stroke/outline color RGB
        stroke_width: Stroke width in pixels
        font_name: Font filename
        align: Text alignment ("left", "center", "right")
        
    Returns:
        NumPy array (RGBA)
    """
    width, height = size
    
    # Create image with transparency
    if bg_color:
        img = Image.new('RGBA', size, bg_color)
    else:
        img = Image.new('RGBA', size, (0, 0, 0, 0))
    
    draw = ImageDraw.Draw(img)
    
    # Try to load font, fallback to default
    try:
        font = ImageFont.truetype(font_name, font_size)
    except:
        try:
            # Try common Windows fonts
            fonts = [
                "C:/Windows/Fonts/impact.ttf",
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/arialbd.ttf"
            ]
            font = None
            for font_path in fonts:
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    break
                except:
                    continue
            
            if font is None:
                font = ImageFont.load_default()
                logger.warning("Using default font")
        except:
            font = ImageFont.load_default()
    
    # Calculate text position
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    if align == "center":
        x = (width - text_width) // 2
    elif align == "right":
        x = width - text_width - 20
    else:  # left
        x = 20
    
    y = (height - text_height) // 2
    
    # Draw text with stroke
    if stroke_color and stroke_width > 0:
        # Draw stroke (outline)
        for adj_x in range(-stroke_width, stroke_width + 1):
            for adj_y in range(-stroke_width, stroke_width + 1):
                draw.text(
                    (x + adj_x, y + adj_y),
                    text,
                    font=font,
                    fill=(*stroke_color, 255)
                )
    
    # Draw main text
    draw.text((x, y), text, font=font, fill=(*color, 255))
    
    # Convert to numpy array
    return np.array(img)


def create_multiline_text_image(
    text: str,
    size: Tuple[int, int],
    font_size: int = 80,
    color: Tuple[int, int, int] = (255, 255, 255),
    **kwargs
) -> np.ndarray:
    """Create multi-line text image"""
    lines = text.split('\n')
    line_height = font_size + 20
    
    # Create main image
    width, height = size
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    
    # Draw each line
    y_offset = (height - (len(lines) * line_height)) // 2
    
    for i, line in enumerate(lines):
        line_img = create_text_image(
            line.strip(),
            (width, line_height),
            font_size=font_size,
            color=color,
            **kwargs
        )
        
        # Paste onto main image
        line_pil = Image.fromarray(line_img)
        img.paste(line_pil, (0, y_offset + i * line_height), line_pil)
    
    return np.array(img)


# Export
__all__ = ['create_text_image', 'create_multiline_text_image']



