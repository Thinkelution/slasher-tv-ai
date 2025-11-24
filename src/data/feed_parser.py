"""
CSV Feed Parser for motorcycle inventory data
"""

import pandas as pd
from typing import List, Optional
from pathlib import Path
from datetime import datetime
import logging

from .data_models import MotorcycleListing

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeedParser:
    """Parse motorcycle inventory CSV feeds"""

    def __init__(self, csv_path: str):
        """
        Initialize feed parser

        Args:
            csv_path: Path to CSV feed file
        """
        self.csv_path = Path(csv_path)
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV feed not found: {csv_path}")

    def parse(self) -> List[MotorcycleListing]:
        """
        Parse CSV feed and return list of motorcycle listings

        Returns:
            List of MotorcycleListing objects
        """
        logger.info(f"Parsing feed: {self.csv_path}")

        try:
            # Read CSV with pandas
            df = pd.read_csv(self.csv_path)
            logger.info(f"Loaded {len(df)} rows from CSV")

            # Parse each row into MotorcycleListing
            listings = []
            for idx, row in df.iterrows():
                try:
                    listing = self._parse_row(row)
                    if listing:
                        listings.append(listing)
                except Exception as e:
                    logger.warning(f"Failed to parse row {idx}: {e}")
                    continue

            logger.info(f"Successfully parsed {len(listings)} listings")
            return listings

        except Exception as e:
            logger.error(f"Failed to parse CSV: {e}")
            raise

    def _parse_row(self, row: pd.Series) -> Optional[MotorcycleListing]:
        """
        Parse single CSV row into MotorcycleListing

        Args:
            row: Pandas Series representing CSV row

        Returns:
            MotorcycleListing object or None if parsing fails
        """
        try:
            # Map CSV columns to model fields
            listing_data = {
                'dealer_id': str(row.get('DealerId', '')),
                'vin': str(row.get('VIN', '')),
                'stock_number': str(row.get('Stock #', '')),
                'condition': str(row.get('New/Used', 'U')),
                'year': int(row.get('Year', 0)),
                'make': str(row.get('Make', '')),
                'model': str(row.get('Model', '')),
                'model_number': self._get_optional_str(row, 'Model Number'),
                'series': self._get_optional_str(row, 'Series'),
                'body': self._get_optional_str(row, 'Body'),
                'transmission': self._get_optional_str(row, 'Transmission'),
                'odometer': self._get_optional_int(row, 'Odometer'),
                'engine_displacement': self._get_optional_str(row, 'Engine Displacement'),
                'engine_cylinder_count': self._get_optional_int(row, 'Engine Cylinder Ct'),
                'drivetrain': self._get_optional_str(row, 'Drivetrain Desc'),
                'color': self._get_optional_str(row, 'Color'),
                'interior_color': self._get_optional_str(row, 'Interior Color'),
                'invoice': self._get_optional_float(row, 'Invoice'),
                'msrp': self._get_optional_float(row, 'MSRP'),
                'book_value': self._get_optional_float(row, 'Book Value'),
                'price': float(row.get('Price', 0)),
                'internet_price': self._get_optional_float(row, 'Internet Price'),
                'inventory_date': self._parse_date(row.get('Inventory Date')),
                'certified': str(row.get('Certified', '')).lower() in ['yes', 'true', '1'],
                'description': self._get_optional_str(row, 'Description'),
                'features': self._get_optional_str(row, 'Features'),
                'photo_urls': str(row.get('Photo Url List', '')),
                'listing_url': self._get_optional_str(row, 'Listing Url'),
                'product_type': str(row.get('Product Type', 'Motorcycles')),
                'bit': self._get_optional_str(row, 'Bit'),
            }

            # Create and validate listing
            listing = MotorcycleListing(**listing_data)
            return listing

        except Exception as e:
            logger.warning(f"Error parsing row: {e}")
            return None

    def _get_optional_str(self, row: pd.Series, column: str) -> Optional[str]:
        """Get optional string value from row"""
        value = row.get(column)
        if pd.isna(value) or value == '#N/A' or value == '':
            return None
        return str(value).strip()

    def _get_optional_int(self, row: pd.Series, column: str) -> Optional[int]:
        """Get optional integer value from row"""
        value = row.get(column)
        if pd.isna(value) or value == '#N/A' or value == '':
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None

    def _get_optional_float(self, row: pd.Series, column: str) -> Optional[float]:
        """Get optional float value from row"""
        value = row.get(column)
        if pd.isna(value) or value == '#N/A' or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _parse_date(self, date_str) -> datetime:
        """Parse date string to datetime"""
        if pd.isna(date_str):
            return datetime.now()

        try:
            # Try parsing common date formats
            return pd.to_datetime(date_str)
        except:
            return datetime.now()

    def filter_by_dealer(self, listings: List[MotorcycleListing], dealer_id: str) -> List[MotorcycleListing]:
        """Filter listings by dealer ID"""
        return [l for l in listings if l.dealer_id == dealer_id]

    def filter_by_price_range(
        self,
        listings: List[MotorcycleListing],
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[MotorcycleListing]:
        """Filter listings by price range"""
        filtered = listings
        if min_price is not None:
            filtered = [l for l in filtered if l.price >= min_price]
        if max_price is not None:
            filtered = [l for l in filtered if l.price <= max_price]
        return filtered

    def filter_by_year(
        self,
        listings: List[MotorcycleListing],
        min_year: Optional[int] = None,
        max_year: Optional[int] = None
    ) -> List[MotorcycleListing]:
        """Filter listings by year"""
        filtered = listings
        if min_year is not None:
            filtered = [l for l in filtered if l.year >= min_year]
        if max_year is not None:
            filtered = [l for l in filtered if l.year <= max_year]
        return filtered


# Example usage
if __name__ == "__main__":
    # Parse feed
    parser = FeedParser("sample-feed.csv")
    listings = parser.parse()

    print(f"\nTotal listings: {len(listings)}")

    # Show first listing
    if listings:
        first = listings[0]
        print(f"\nFirst listing:")
        print(f"  {first.display_name}")
        print(f"  Price: ${first.price:,.0f}")
        print(f"  Photos: {len(first.photo_urls)}")
        print(f"  Stock: {first.stock_number}")
