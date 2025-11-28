#!/usr/bin/env python
"""
Slasher TV AI - Quick Run Script
================================
Simple entry point for the video generation pipeline.

Usage:
    python run.py                    # Process all listings
    python run.py --limit 1          # Process first listing only
    python run.py --skip-video       # Assets only (no video)
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.main import SlasherTVPipeline
import argparse


def main():
    parser = argparse.ArgumentParser(description="Slasher TV AI - Quick Run")
    parser.add_argument("--limit", type=int, default=1, help="Number of listings (default: 1)")
    parser.add_argument("--skip-video", action="store_true", help="Skip video generation")
    parser.add_argument("--template", default="dark", help="Video template")
    args = parser.parse_args()
    
    print("="*60)
    print("SLASHER TV AI - MOTORCYCLE VIDEO GENERATOR")
    print("="*60)
    
    pipeline = SlasherTVPipeline(
        csv_path="sample-feed.csv",
        assets_dir="./assets",
        output_dir="./output",
        template=args.template
    )
    
    pipeline.run(limit=args.limit, skip_video=args.skip_video)


if __name__ == "__main__":
    main()

