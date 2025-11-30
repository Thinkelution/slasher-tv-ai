"""
Voice Generator using ElevenLabs AI
Professional male bold voice for TV advertisements
"""

import os
from pathlib import Path
from typing import Optional, Literal
import logging
import requests

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ElevenLabs API Configuration
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1"

# Recommended voices for TV commercial (bold male voices)
VOICE_PRESETS = {
    # Deep, authoritative male voices ideal for TV commercials
    "adam": "pNInz6obpgDQGcFmaJgB",      # Deep, narrative voice
    "arnold": "VR6AewLTigWG4xSOukaG",    # Strong, bold voice  
    "josh": "TxGEqnHWrfWFTfGW9XjX",      # Deep, dramatic voice
    "sam": "yoZ06aMxZJJ28mfd3POQ",       # Confident, authoritative
    "marcus": "xkBjKPxqt9ZFz4HUALnM",    # Bold announcer style (custom)
}

# Default voice for TV commercials - deep, bold, authoritative
DEFAULT_VOICE = "adam"


class VoiceGenerator:
    """Generate professional voiceovers using ElevenLabs AI"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        voice_id: Optional[str] = None,
        voice_name: str = DEFAULT_VOICE
    ):
        """
        Initialize voice generator with ElevenLabs

        Args:
            api_key: ElevenLabs API key (or use ELEVENLABS_API_KEY env var)
            voice_id: Specific voice ID (overrides voice_name)
            voice_name: Voice preset name ('adam', 'arnold', 'josh', 'sam')
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ElevenLabs API key required. Set ELEVENLABS_API_KEY env variable.")

        # Set voice ID
        if voice_id:
            self.voice_id = voice_id
        else:
            self.voice_id = VOICE_PRESETS.get(voice_name, VOICE_PRESETS[DEFAULT_VOICE])

        self.voice_name = voice_name
        logger.info(f"Initialized VoiceGenerator with voice: {voice_name}")

    def generate_voiceover(
        self,
        script: str,
        output_path: Path,
        stability: float = 0.35,
        similarity_boost: float = 0.75,
        style: float = 0.45,
        model: str = "eleven_multilingual_v2"
    ) -> Path:
        """
        Generate professional voiceover from script

        Args:
            script: Text script to convert to speech
            output_path: Path to save audio file (MP3)
            stability: Voice stability (0.0-1.0) - lower = more expressive
            similarity_boost: Voice clarity (0.0-1.0) - higher = clearer
            style: Style exaggeration (0.0-1.0) - for dramatic effect
            model: ElevenLabs model to use

        Returns:
            Path to generated audio file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # API endpoint for text-to-speech
        url = f"{ELEVENLABS_API_URL}/text-to-speech/{self.voice_id}"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }

        # Voice settings optimized for bold TV commercial delivery
        payload = {
            "text": script,
            "model_id": model,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
                "use_speaker_boost": True  # Enhances voice clarity
            }
        }

        try:
            logger.info(f"Generating voiceover ({len(script.split())} words)...")
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()

            # Save audio file
            with open(output_path, "wb") as f:
                f.write(response.content)

            logger.info(f"✓ Voiceover saved: {output_path}")
            return output_path

        except requests.exceptions.HTTPError as e:
            logger.error(f"ElevenLabs API error: {e}")
            logger.error(f"Response: {response.text}")
            raise
        except Exception as e:
            logger.error(f"Failed to generate voiceover: {e}")
            raise

    def generate_tv_commercial(
        self,
        script: str,
        output_path: Path,
        style: Literal["aggressive", "smooth", "professional"] = "aggressive"
    ) -> Path:
        """
        Generate TV commercial voiceover with optimized settings

        Args:
            script: Commercial script text
            output_path: Path to save audio file
            style: Commercial style affecting voice parameters

        Returns:
            Path to generated audio file
        """
        # Voice settings optimized for each commercial style
        style_settings = {
            "aggressive": {
                "stability": 0.30,       # More dynamic, energetic
                "similarity_boost": 0.80,
                "style": 0.55            # More dramatic
            },
            "smooth": {
                "stability": 0.45,       # More controlled, elegant
                "similarity_boost": 0.75,
                "style": 0.35            # Subtle style
            },
            "professional": {
                "stability": 0.40,       # Balanced delivery
                "similarity_boost": 0.78,
                "style": 0.40            # Moderate style
            }
        }

        settings = style_settings.get(style, style_settings["aggressive"])

        logger.info(f"Generating {style} TV commercial voiceover...")
        return self.generate_voiceover(
            script=script,
            output_path=output_path,
            **settings
        )

    def list_available_voices(self) -> list:
        """List all available voices from ElevenLabs account"""
        url = f"{ELEVENLABS_API_URL}/voices"
        headers = {"xi-api-key": self.api_key}

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            voices = response.json().get("voices", [])

            voice_list = []
            for voice in voices:
                voice_list.append({
                    "name": voice["name"],
                    "voice_id": voice["voice_id"],
                    "category": voice.get("category", "unknown"),
                    "labels": voice.get("labels", {})
                })
                logger.info(f"  {voice['name']}: {voice['voice_id']}")

            return voice_list

        except Exception as e:
            logger.error(f"Failed to list voices: {e}")
            return []

    def get_voice_info(self) -> dict:
        """Get information about the current voice"""
        url = f"{ELEVENLABS_API_URL}/voices/{self.voice_id}"
        headers = {"xi-api-key": self.api_key}

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get voice info: {e}")
            return {}

    def estimate_cost(self, script: str) -> dict:
        """Estimate API cost for generating voiceover"""
        char_count = len(script)
        # ElevenLabs pricing: approximately $0.30 per 1000 characters (varies by plan)
        estimated_cost = (char_count / 1000) * 0.30
        
        return {
            "characters": char_count,
            "words": len(script.split()),
            "estimated_duration_sec": len(script.split()) / 2.5,
            "estimated_cost_usd": round(estimated_cost, 4)
        }


# Example usage and testing
if __name__ == "__main__":
    # Test script - professional 30-second TV commercial
    test_script = """Power. Unleashed.

The twenty twenty-four Harley-Davidson Low Rider ST. Raw American muscle meets precision engineering. A Milwaukee-Eight one seventeen engine that doesn't just rumble. It roars.

Finished in stunning Billiard Gray. Only three hundred seventy-seven miles. Pristine condition.

Now. Just twenty-seven thousand nine hundred ninety dollars.

Legends like this don't wait. Neither should you.

Scan to reserve. San Diego Harley-Davidson."""

    # Initialize generator
    generator = VoiceGenerator(voice_name="adam")

    # Show cost estimate
    estimate = generator.estimate_cost(test_script)
    print(f"\nScript Analysis:")
    print(f"  Characters: {estimate['characters']}")
    print(f"  Words: {estimate['words']}")
    print(f"  Est. Duration: {estimate['estimated_duration_sec']:.1f} seconds")
    print(f"  Est. Cost: ${estimate['estimated_cost_usd']:.4f}")

    # Generate voiceover
    output_file = Path("./test_voiceover.mp3")
    try:
        result = generator.generate_tv_commercial(
            script=test_script,
            output_path=output_file,
            style="aggressive"
        )
        print(f"\n✓ Voiceover generated: {result}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("  Make sure ELEVENLABS_API_KEY is set in your environment or .env file")



