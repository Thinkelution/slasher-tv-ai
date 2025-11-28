"""
Main Video Composer - Orchestrates video generation
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
import json

try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

from .templates.simple_dark_template import SimpleDarkTemplate as DarkTemplate
from .audio_mixer import AudioMixer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoComposer:
    """Main video composition engine"""
    
    def __init__(
        self,
        template: str = "dark",
        resolution: tuple = (1920, 1080),
        fps: int = 30,
        duration: float = 30.0,
        output_dir: str = "./output"
    ):
        """
        Initialize video composer
        
        Args:
            template: Template name ("dark", "clean", "fire")
            resolution: Video resolution (width, height)
            fps: Frames per second
            duration: Video duration in seconds
            output_dir: Output directory for videos
        """
        if not MOVIEPY_AVAILABLE:
            raise ImportError("MoviePy not available. Run: pip install moviepy")
        
        self.template_name = template
        self.resolution = resolution
        self.fps = fps
        self.duration = duration
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize template
        self.template = self._load_template(template)
        
        # Initialize audio mixer
        self.audio_mixer = AudioMixer(
            voiceover_volume=1.0,
            music_volume=0.25,
            duck_music=True
        )
        
        logger.info(
            f"Initialized VideoComposer "
            f"(template: {template}, {resolution[0]}x{resolution[1]} @ {fps}fps)"
        )
    
    def _load_template(self, template_name: str):
        """Load video template"""
        templates = {
            'dark': DarkTemplate,
            # Add more templates here
            # 'clean': CleanTemplate,
            # 'fire': FireTemplate,
        }
        
        if template_name not in templates:
            logger.warning(f"Template '{template_name}' not found, using 'dark'")
            template_name = 'dark'
        
        template_class = templates[template_name]
        return template_class(
            resolution=self.resolution,
            fps=self.fps,
            duration=self.duration
        )
    
    def create_video(
        self,
        bike_data: Dict[str, Any],
        bike_image: str,
        voiceover: str,
        qr_code: str,
        background_music: Optional[str] = None,
        output_filename: Optional[str] = None
    ) -> str:
        """
        Create complete video from assets
        
        Args:
            bike_data: Dictionary with bike information
            bike_image: Path to processed bike image (transparent background)
            voiceover: Path to voiceover audio
            qr_code: Path to QR code image
            background_music: Path to background music (optional)
            output_filename: Custom output filename (optional)
            
        Returns:
            Path to generated video file
        """
        try:
            logger.info("=" * 60)
            logger.info("Starting video generation...")
            logger.info("=" * 60)
            
            # Validate inputs
            self._validate_inputs(bike_image, voiceover, qr_code)
            
            # Generate output filename
            if not output_filename:
                stock_number = bike_data.get('stock_number', 'video')
                output_filename = f"{stock_number}_{self.template_name}.mp4"
            
            output_path = self.output_dir / output_filename
            
            # Step 1: Create video
            logger.info("\n[1/3] Creating video segments...")
            video = self.template.create_video(
                bike_data=bike_data,
                bike_image=bike_image,
                qr_code=qr_code,
                dealer_name=bike_data.get('dealer_name', 'San Diego Harley-Davidson')
            )
            
            # Step 2: Mix audio
            logger.info("\n[2/3] Mixing audio...")
            audio = self.audio_mixer.mix(
                voiceover_path=voiceover,
                background_music_path=background_music,
                duration=self.duration
            )
            
            # Add fade effects to audio
            audio = self.audio_mixer.add_fade_in(audio, 0.5)
            audio = self.audio_mixer.add_fade_out(audio, 1.0)
            
            # Attach audio to video
            video = video.set_audio(audio)
            
            # Step 3: Export video
            logger.info(f"\n[3/3] Exporting video to: {output_path}")
            video.write_videofile(
                str(output_path),
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                audio_bitrate='192k',
                preset='medium',
                threads=4
            )
            
            # Close clips to free memory
            video.close()
            audio.close()
            
            logger.info("\n" + "=" * 60)
            logger.info("✓ Video generation complete!")
            logger.info(f"  Output: {output_path}")
            logger.info(f"  Size: {output_path.stat().st_size / (1024*1024):.2f} MB")
            logger.info("=" * 60)
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to create video: {e}")
            raise
    
    def create_video_from_listing(
        self,
        listing_dir: str,
        background_music: Optional[str] = None
    ) -> str:
        """
        Create video from listing directory
        
        Args:
            listing_dir: Path to listing directory with all assets
            background_music: Path to background music (optional)
            
        Returns:
            Path to generated video
        """
        listing_path = Path(listing_dir)
        
        # Load metadata
        metadata_path = listing_path / "metadata.json"
        with open(metadata_path, 'r') as f:
            bike_data = json.load(f)
        
        # Find assets
        processed_dir = listing_path / "processed"
        bike_images = list(processed_dir.glob("photo_*_processed.png"))
        
        if not bike_images:
            raise FileNotFoundError(f"No processed images found in {processed_dir}")
        
        # Use first image (hero shot)
        bike_image = str(bike_images[0])
        
        # Other assets
        voiceover = str(listing_path / "voiceover.mp3")
        qr_code = str(listing_path / "qr_code.png")
        
        # Create video
        return self.create_video(
            bike_data=bike_data,
            bike_image=bike_image,
            voiceover=voiceover,
            qr_code=qr_code,
            background_music=background_music
        )
    
    def _validate_inputs(self, bike_image: str, voiceover: str, qr_code: str):
        """Validate input files exist"""
        files = {
            'bike_image': bike_image,
            'voiceover': voiceover,
            'qr_code': qr_code
        }
        
        for name, path in files.items():
            if not Path(path).exists():
                raise FileNotFoundError(f"{name} not found: {path}")
    
    def batch_create_videos(
        self,
        listings_dir: str,
        background_music: Optional[str] = None,
        limit: Optional[int] = None
    ) -> list:
        """
        Create videos for multiple listings
        
        Args:
            listings_dir: Directory containing listing subdirectories
            background_music: Path to background music (optional)
            limit: Maximum number of videos to create (optional)
            
        Returns:
            List of paths to generated videos
        """
        listings_path = Path(listings_dir)
        
        # Find all listing directories
        listing_dirs = []
        for dealer_dir in listings_path.iterdir():
            if dealer_dir.is_dir():
                for listing_dir in dealer_dir.iterdir():
                    if listing_dir.is_dir():
                        listing_dirs.append(listing_dir)
        
        if limit:
            listing_dirs = listing_dirs[:limit]
        
        logger.info(f"Found {len(listing_dirs)} listings to process")
        
        # Process each listing
        videos = []
        for i, listing_dir in enumerate(listing_dirs, 1):
            try:
                logger.info(f"\nProcessing listing {i}/{len(listing_dirs)}: {listing_dir.name}")
                
                video_path = self.create_video_from_listing(
                    str(listing_dir),
                    background_music
                )
                
                videos.append(video_path)
                logger.info(f"✓ Created video {i}/{len(listing_dirs)}")
                
            except Exception as e:
                logger.error(f"✗ Failed to create video for {listing_dir.name}: {e}")
                continue
        
        logger.info(f"\nBatch complete: {len(videos)}/{len(listing_dirs)} videos created")
        return videos


# Example usage
if __name__ == "__main__":
    print("Video Composer - Test Suite")
    print("=" * 60)
    
    if not MOVIEPY_AVAILABLE:
        print("✗ MoviePy not available")
        print("  Run: pip install moviepy")
        exit(1)
    
    print("✓ MoviePy available")
    
    # Initialize composer
    composer = VideoComposer(
        template="dark",
        resolution=(1920, 1080),
        fps=30,
        duration=30.0,
        output_dir="./output"
    )
    
    print("\n✓ VideoComposer initialized")
    print(f"  Template: dark")
    print(f"  Resolution: 1920x1080")
    print(f"  FPS: 30")
    print(f"  Duration: 30s")
    
    print("\nFeatures available:")
    print("  - Dark template (aggressive, dramatic)")
    print("  - Audio mixing (voiceover + music)")
    print("  - H.264 encoding")
    print("  - Batch processing")
    
    print("\nReady to create videos!")
    print("\nUsage:")
    print("  from src.video import VideoComposer")
    print("  composer = VideoComposer()")
    print("  video = composer.create_video_from_listing('assets/4802/156359BB')")
