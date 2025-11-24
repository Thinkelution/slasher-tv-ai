"""
Data models for Slasher TV AI video generation system
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, validator


class MotorcycleListing(BaseModel):
    """Model for individual motorcycle listing from dealer feed"""

    # Identifiers
    dealer_id: str = Field(..., description="Dealer identifier")
    vin: str = Field(..., description="Vehicle Identification Number")
    stock_number: str = Field(..., description="Dealer stock number")

    # Basic Info
    condition: str = Field(..., description="New (N) or Used (U)")
    year: int = Field(..., description="Model year")
    make: str = Field(..., description="Manufacturer (e.g., Harley-Davidson)")
    model: str = Field(..., description="Model name")
    model_number: Optional[str] = Field(None, description="Specific model number")
    series: Optional[str] = Field(None, description="Series/trim level")

    # Specifications
    body: Optional[str] = Field(None, description="Body type")
    transmission: Optional[str] = Field(None, description="Transmission type")
    odometer: Optional[int] = Field(None, description="Mileage")
    engine_displacement: Optional[str] = Field(None, description="Engine size (e.g., 117 cubic inches)")
    engine_cylinder_count: Optional[int] = Field(None, description="Number of cylinders")
    drivetrain: Optional[str] = Field(None, description="Drivetrain description")

    # Appearance
    color: Optional[str] = Field(None, description="Exterior color")
    interior_color: Optional[str] = Field(None, description="Interior/seat color")

    # Pricing
    invoice: Optional[float] = Field(None, description="Invoice price")
    msrp: Optional[float] = Field(None, description="Manufacturer's suggested retail price")
    book_value: Optional[float] = Field(None, description="Book value")
    price: float = Field(..., description="Listing price")
    internet_price: Optional[float] = Field(None, description="Special internet price")

    # Details
    inventory_date: datetime = Field(..., description="Date added to inventory")
    certified: bool = Field(default=False, description="Certified pre-owned")
    description: Optional[str] = Field(None, description="Full listing description")
    features: Optional[str] = Field(None, description="Feature list")

    # Media
    photo_urls: List[str] = Field(default_factory=list, description="List of photo URLs")
    listing_url: Optional[str] = Field(None, description="Online listing URL")

    # Metadata
    product_type: str = Field(default="Motorcycles", description="Product type")
    bit: Optional[str] = Field(None, description="Additional bit field")

    @validator('photo_urls', pre=True)
    def split_photo_urls(cls, v):
        """Split comma-separated photo URLs into list"""
        if isinstance(v, str):
            return [url.strip() for url in v.split(',') if url.strip()]
        return v or []

    @validator('condition', pre=True)
    def normalize_condition(cls, v):
        """Normalize condition to full name"""
        if v and v.upper() in ['U', 'USED']:
            return 'Used'
        elif v and v.upper() in ['N', 'NEW']:
            return 'New'
        return v

    @validator('odometer', pre=True)
    def parse_odometer(cls, v):
        """Parse odometer value, handling empty strings"""
        if v in ['', None, '#N/A']:
            return None
        try:
            return int(v)
        except (ValueError, TypeError):
            return None

    @property
    def display_name(self) -> str:
        """Generate display name for the motorcycle"""
        return f"{self.year} {self.make} {self.model}"

    @property
    def short_description(self) -> str:
        """Generate short description for video"""
        parts = [str(self.year), self.make, self.model]
        if self.engine_displacement:
            parts.append(f"- {self.engine_displacement}")
        if self.odometer:
            parts.append(f"- {self.odometer:,} miles")
        return " ".join(parts)

    @property
    def savings(self) -> Optional[float]:
        """Calculate savings if MSRP available"""
        if self.msrp and self.price < self.msrp:
            return self.msrp - self.price
        return None

    @property
    def is_low_mileage(self) -> bool:
        """Check if bike has low mileage (under 5000 miles)"""
        return self.odometer is not None and self.odometer < 5000

    @property
    def is_custom(self) -> bool:
        """Check if bike is custom build"""
        desc_lower = (self.description or '').lower()
        return 'custom' in desc_lower or 'one-of-a-kind' in desc_lower


class VideoMetadata(BaseModel):
    """Metadata for generated video"""

    listing: MotorcycleListing
    video_path: str
    template_used: str
    script: str
    voiceover_path: Optional[str] = None
    qr_code_path: Optional[str] = None
    generation_date: datetime = Field(default_factory=datetime.now)
    duration: float = 30.0
    resolution: str = "1920x1080"

    class Config:
        arbitrary_types_allowed = True


class VideoGenerationJob(BaseModel):
    """Job configuration for video generation"""

    listing: MotorcycleListing
    template: str = "dark"
    voice_style: str = "aggressive"
    background_music: Optional[str] = None
    priority: int = 0

    class Config:
        arbitrary_types_allowed = True
