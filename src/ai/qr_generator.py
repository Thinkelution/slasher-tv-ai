"""
QR Code Generator for motorcycle listings
"""

import qrcode
from PIL import Image
from pathlib import Path
from typing import Optional, Tuple, Union
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QRGenerator:
    """Generate QR codes for motorcycle listings"""

    def __init__(
        self,
        box_size: int = 10,
        border: int = 2,
        fill_color: str = "black",
        back_color: str = "white"
    ):
        """
        Initialize QR code generator

        Args:
            box_size: Size of each QR code box in pixels
            border: Border size in boxes
            fill_color: QR code color
            back_color: Background color
        """
        self.box_size = box_size
        self.border = border
        self.fill_color = fill_color
        self.back_color = back_color

    def generate_qr_code(
        self,
        url: str,
        output_path: Path,
        size: tuple = (300, 300)
    ) -> Path:
        """
        Generate QR code for listing URL

        Args:
            url: Listing URL
            output_path: Path to save QR code image
            size: Final image size (width, height)

        Returns:
            Path to generated QR code
        """
        try:
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=self.box_size,
                border=self.border,
            )

            qr.add_data(url)
            qr.make(fit=True)

            # Create image
            img = qr.make_image(
                fill_color=self.fill_color,
                back_color=self.back_color
            )

            # Resize to target size
            img = img.resize(size, Image.Resampling.LANCZOS)

            # Save
            output_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(output_path)

            logger.info(f"Generated QR code: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate QR code: {e}")
            raise

    def generate_with_logo(
        self,
        url: str,
        output_path: Path,
        logo_path: Optional[Path] = None,
        size: tuple = (300, 300)
    ) -> Path:
        """
        Generate QR code with embedded logo

        Args:
            url: Listing URL
            output_path: Path to save QR code image
            logo_path: Path to logo image (optional)
            size: Final image size

        Returns:
            Path to generated QR code
        """
        # Generate base QR code
        qr_path = self.generate_qr_code(url, output_path, size)

        # If no logo, return base QR
        if not logo_path or not logo_path.exists():
            return qr_path

        try:
            # Open QR code
            qr_img = Image.open(qr_path)

            # Open and resize logo
            logo = Image.open(logo_path)
            logo_size = min(size[0] // 4, size[1] // 4)
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

            # Calculate logo position (center)
            logo_pos = (
                (qr_img.size[0] - logo.size[0]) // 2,
                (qr_img.size[1] - logo.size[1]) // 2
            )

            # Paste logo onto QR code
            if logo.mode == 'RGBA':
                qr_img.paste(logo, logo_pos, logo)
            else:
                qr_img.paste(logo, logo_pos)

            # Save
            qr_img.save(output_path)

            logger.info(f"Generated QR code with logo: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to add logo to QR code: {e}")
            return qr_path  # Return QR without logo


# Example usage
if __name__ == "__main__":
    generator = QRGenerator()

    # Test URL
    test_url = "https://sandiegoharley.com/inventory/791934/harley-davidson-sporster-883-custom"

    # Generate QR code
    output = Path("./test_qr.png")
    generator.generate_qr_code(test_url, output, size=(400, 400))

    print(f"QR code generated: {output}")
