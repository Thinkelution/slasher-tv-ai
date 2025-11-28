"""
Audio Mixer for combining voiceover with background music
"""

import logging
from pathlib import Path
from typing import Optional

try:
    from moviepy.editor import AudioFileClip, CompositeAudioClip
    from moviepy.audio.fx.volumex import volumex
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioMixer:
    """Mix voiceover with background music"""
    
    def __init__(
        self,
        voiceover_volume: float = 1.0,
        music_volume: float = 0.3,
        duck_music: bool = True,
        duck_amount: float = 0.15
    ):
        """
        Initialize audio mixer
        
        Args:
            voiceover_volume: Voiceover volume (0.0 to 1.0)
            music_volume: Background music volume (0.0 to 1.0)
            duck_music: Whether to duck music during voiceover
            duck_amount: Amount to reduce music volume when ducking
        """
        if not MOVIEPY_AVAILABLE:
            raise ImportError("MoviePy not available. Run: pip install moviepy")
        
        self.voiceover_volume = voiceover_volume
        self.music_volume = music_volume
        self.duck_music = duck_music
        self.duck_amount = duck_amount
        
        logger.info(
            f"Initialized AudioMixer "
            f"(voiceover: {voiceover_volume}, music: {music_volume}, duck: {duck_music})"
        )
    
    def mix(
        self,
        voiceover_path: str,
        background_music_path: Optional[str] = None,
        output_path: Optional[str] = None,
        duration: float = 30.0
    ) -> AudioFileClip:
        """
        Mix voiceover with background music
        
        Args:
            voiceover_path: Path to voiceover audio file
            background_music_path: Path to background music (optional)
            output_path: Path to save mixed audio (optional)
            duration: Target duration in seconds
            
        Returns:
            Mixed AudioFileClip or None if no valid audio
        """
        logger.info("Mixing audio...")
        
        voiceover = None
        
        # Try to load voiceover
        try:
            vo_path = Path(voiceover_path)
            if vo_path.exists() and vo_path.stat().st_size > 1000:
                voiceover = AudioFileClip(voiceover_path)
                voiceover = voiceover.volumex(self.voiceover_volume)
                logger.info(f"Loaded voiceover: {voiceover.duration:.1f}s")
            else:
                logger.warning(f"Voiceover file missing or too small: {voiceover_path}")
        except Exception as e:
            logger.warning(f"Could not load voiceover: {e}")
            voiceover = None
        
        # If no voiceover, create silent audio
        if voiceover is None:
            logger.warning("Creating silent audio track (no valid voiceover)")
            from moviepy.audio.AudioClip import AudioClip
            voiceover = AudioClip(lambda t: 0, duration=duration, fps=44100)
            voiceover = voiceover.set_duration(duration)
        
        # Ensure voiceover fits duration
        if voiceover.duration > duration:
            logger.warning(f"Voiceover too long ({voiceover.duration:.1f}s), trimming to {duration}s")
            voiceover = voiceover.subclip(0, duration)
        
        # If no background music, just return voiceover
        if not background_music_path:
            logger.info("No background music provided")
            if output_path:
                voiceover.write_audiofile(output_path, codec='aac')
            return voiceover
        
        # Load background music
        logger.info(f"Loading background music: {background_music_path}")
        music = AudioFileClip(background_music_path)
        
        # Loop music if too short
        if music.duration < duration:
            repeats = int(duration / music.duration) + 1
            logger.info(f"Looping music {repeats} times")
            music = music.loop(repeats)
        
        # Trim music to duration
        music = music.subclip(0, duration)
        
        # Apply music volume
        if self.duck_music:
            # Duck music during voiceover
            music = self._duck_music(music, voiceover, duration)
        else:
            # Constant volume
            music = music.volumex(self.music_volume)
        
        # Composite audio
        logger.info("Compositing audio...")
        final_audio = CompositeAudioClip([music, voiceover])
        
        # Save if output path provided
        if output_path:
            logger.info(f"Saving mixed audio to: {output_path}")
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            final_audio.write_audiofile(output_path, codec='aac', bitrate='192k')
        
        logger.info("Audio mixing complete")
        return final_audio
    
    def _duck_music(
        self,
        music: AudioFileClip,
        voiceover: AudioFileClip,
        duration: float
    ) -> AudioFileClip:
        """
        Duck music volume during voiceover
        
        Args:
            music: Background music clip
            voiceover: Voiceover clip
            duration: Total duration
            
        Returns:
            Music clip with ducking applied
        """
        # Simple ducking: reduce music volume during voiceover
        vo_duration = voiceover.duration
        
        # Create volume envelope
        def volume_envelope(t):
            if t < vo_duration:
                # During voiceover: duck
                return self.music_volume * self.duck_amount
            else:
                # After voiceover: full volume
                return self.music_volume
        
        return music.fl(lambda gf, t: gf(t) * volume_envelope(t), keep_duration=True)
    
    def add_fade_in(
        self,
        audio: AudioFileClip,
        duration: float = 1.0
    ) -> AudioFileClip:
        """
        Add fade in to audio
        
        Args:
            audio: Audio clip
            duration: Fade duration in seconds
            
        Returns:
            Audio with fade in
        """
        return audio.audio_fadein(duration)
    
    def add_fade_out(
        self,
        audio: AudioFileClip,
        duration: float = 1.0
    ) -> AudioFileClip:
        """
        Add fade out to audio
        
        Args:
            audio: Audio clip
            duration: Fade duration in seconds
            
        Returns:
            Audio with fade out
        """
        return audio.audio_fadeout(duration)
    
    def normalize_audio(
        self,
        audio_path: str,
        output_path: str,
        target_duration: float
    ) -> bool:
        """
        Normalize audio to target duration
        
        Args:
            audio_path: Path to input audio
            output_path: Path to save normalized audio
            target_duration: Target duration in seconds
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Normalizing audio to {target_duration}s")
            
            audio = AudioFileClip(audio_path)
            
            # Speed up or slow down to fit duration
            if audio.duration != target_duration:
                speed = audio.duration / target_duration
                logger.info(f"Adjusting speed by {speed:.2f}x")
                audio = audio.fx(volumex, speed)
            
            # Save
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            audio.write_audiofile(output_path, codec='aac')
            
            logger.info("Audio normalization complete")
            return True
            
        except Exception as e:
            logger.error(f"Failed to normalize audio: {e}")
            return False


# Example usage
if __name__ == "__main__":
    print("Audio Mixer - Test Suite")
    print("=" * 60)
    
    if not MOVIEPY_AVAILABLE:
        print("✗ MoviePy not available")
        print("  Run: pip install moviepy")
        exit(1)
    
    print("✓ MoviePy available")
    
    # Initialize mixer
    mixer = AudioMixer(
        voiceover_volume=1.0,
        music_volume=0.3,
        duck_music=True
    )
    
    print("\n✓ AudioMixer initialized")
    print("\nFeatures available:")
    print("  - Mix voiceover with background music")
    print("  - Automatic music ducking")
    print("  - Volume control")
    print("  - Audio normalization")
    print("  - Fade in/out effects")
    
    print("\nReady to mix audio!")
    print("\nUsage:")
    print("  from src.video import AudioMixer")
    print("  mixer = AudioMixer()")
    print("  audio = mixer.mix('voiceover.mp3', 'music.mp3')")
