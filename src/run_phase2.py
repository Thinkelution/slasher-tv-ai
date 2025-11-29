"""
Phase 2: AI Generation Layer - Script & Voice Generation
Generates professional 30-second TV commercial scripts and voiceovers
"""

import sys
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data import FeedParser, AssetManager
from src.ai import ScriptGenerator, VoiceGenerator, QRGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_phase2(
    csv_path: str = "sample-feed.csv",
    listing_index: int = 0,
    style: str = "aggressive",
    voice: str = "adam"
):
    """
    Execute Phase 2: AI Content Generation Pipeline
    
    1. Load listing from Phase 1
    2. Generate professional 30-second script (OpenAI)
    3. Generate voiceover audio (ElevenLabs)
    4. Generate QR code for listing URL
    """
    logger.info("=" * 60)
    logger.info("PHASE 2: AI GENERATION LAYER")
    logger.info("=" * 60)
    
    # Initialize components
    parser = FeedParser(csv_path)
    asset_manager = AssetManager(assets_dir="./assets")
    
    # Step 1: Load listing
    logger.info("\n[Step 1/4] Loading listing...")
    listings = parser.parse()
    
    if listing_index >= len(listings):
        logger.error(f"Listing index {listing_index} out of range (max: {len(listings)-1})")
        return
    
    listing = listings[listing_index]
    listing_dir = asset_manager.get_listing_dir(listing)
    
    print(f"\n🏍️  SELECTED LISTING:")
    print(f"   {listing.display_name}")
    print(f"   Stock #: {listing.stock_number}")
    print(f"   Price: ${listing.price:,.0f}")
    print(f"   Directory: {listing_dir}")
    
    # Step 2: Generate Script
    logger.info("\n[Step 2/4] Generating professional script (OpenAI)...")
    try:
        script_gen = ScriptGenerator(provider="openai")
        script = script_gen.generate_script(
            year=listing.year,
            make=listing.make,
            model=listing.model,
            price=listing.price,
            description=listing.description,
            color=listing.color,
            mileage=listing.odometer,
            engine=listing.engine_displacement,
            is_custom=listing.is_custom,
            style=style
        )
        
        # Save script
        script_path = asset_manager.get_script_path(listing)
        script_path.parent.mkdir(parents=True, exist_ok=True)
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script)
        
        # Calculate duration estimate
        word_count = len(script.split())
        duration_est = script_gen.get_script_duration_estimate(script)
        
        print(f"\n📝 GENERATED SCRIPT ({word_count} words, ~{duration_est:.1f}s):")
        print("-" * 60)
        print(script)
        print("-" * 60)
        print(f"   Saved to: {script_path}")
        
    except Exception as e:
        logger.error(f"Script generation failed: {e}")
        print(f"\n⚠️  Script generation failed: {e}")
        print("   Make sure OPENAI_API_KEY is set in your .env file")
        script = None
    
    # Step 3: Generate Voiceover
    if script:
        logger.info("\n[Step 3/4] Generating voiceover (ElevenLabs)...")
        try:
            voice_gen = VoiceGenerator(voice_name=voice)
            audio_path = asset_manager.get_audio_path(listing, "voiceover")
            
            # Show cost estimate
            estimate = voice_gen.estimate_cost(script)
            print(f"\n🎙️  VOICEOVER GENERATION:")
            print(f"   Voice: {voice}")
            print(f"   Est. Duration: {estimate['estimated_duration_sec']:.1f} seconds")
            print(f"   Est. Cost: ${estimate['estimated_cost_usd']:.4f}")
            
            # Generate voiceover
            voice_gen.generate_tv_commercial(
                script=script,
                output_path=audio_path,
                style=style
            )
            
            print(f"   ✓ Audio saved: {audio_path}")
            
        except Exception as e:
            logger.error(f"Voiceover generation failed: {e}")
            print(f"\n⚠️  Voiceover generation failed: {e}")
            print("   Make sure ELEVENLABS_API_KEY is set in your .env file")
    else:
        logger.info("\n[Step 3/4] Skipping voiceover (no script)...")
    
    # Step 4: Generate QR Code
    logger.info("\n[Step 4/4] Generating QR code...")
    if listing.listing_url:
        try:
            qr_gen = QRGenerator()
            qr_path = asset_manager.get_qr_code_path(listing)
            qr_gen.generate_qr_code(
                url=listing.listing_url,
                output_path=qr_path,
                size=(400, 400)
            )
            print(f"\n📱 QR CODE:")
            print(f"   URL: {listing.listing_url}")
            print(f"   ✓ Saved: {qr_path}")
        except Exception as e:
            logger.error(f"QR code generation failed: {e}")
    else:
        print("\n📱 QR CODE: No listing URL available")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("PHASE 2 COMPLETE")
    logger.info("=" * 60)
    
    summary = asset_manager.get_asset_summary(listing)
    print(f"\n📊 ASSET SUMMARY:")
    print(f"   Directory: {summary['listing_dir']}")
    print(f"   Images: {summary['images']}")
    print(f"   Script: {'✓' if summary['has_script'] else '✗'}")
    print(f"   Voiceover: {'✓' if summary['has_voiceover'] else '✗'}")
    print(f"   QR Code: {'✓' if summary['has_qr_code'] else '✗'}")
    
    return listing, script


if __name__ == "__main__":
    import argparse
    
    argparser = argparse.ArgumentParser(description="Phase 2: AI Content Generation")
    argparser.add_argument("--csv", default="sample-feed.csv", help="CSV feed path")
    argparser.add_argument("--index", type=int, default=0, help="Listing index (0-based)")
    argparser.add_argument("--style", choices=["aggressive", "smooth", "professional"], 
                          default="aggressive", help="Script/voice style")
    argparser.add_argument("--voice", choices=["dan", "adam", "arnold", "josh", "sam"],
                          default="dan", help="ElevenLabs voice preset (dan=enthusiastic salesman)")
    
    args = argparser.parse_args()
    run_phase2(
        csv_path=args.csv,
        listing_index=args.index,
        style=args.style,
        voice=args.voice
    )

