"""
AI Voice Generator (Text-to-Speech) for motorcycle promo videos
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict
from enum import Enum

try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import VoiceSettings
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import azure.cognitiveservices.speech as speechsdk
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

try:
    from google.cloud import texttospeech
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceStyle(Enum):
    """Voice style options matching script styles"""
    AGGRESSIVE = "aggressive"  # High-energy, commanding
    SMOOTH = "smooth"          # Sophisticated, elegant
    PROFESSIONAL = "professional"  # Clear, trustworthy


class VoiceProvider(Enum):
    """Available TTS providers"""
    ELEVENLABS = "elevenlabs"  # Premium quality
    AZURE = "azure"            # Microsoft Azure TTS
    GOOGLE = "google"          # Google Cloud TTS
    GTTS = "gtts"             # Google TTS (free)
    PYTTSX3 = "pyttsx3"       # Offline TTS
    AUTO = "auto"             # Auto-select best available


class VoiceGenerator:
    """Generate professional voiceovers for motorcycle videos"""

    # ElevenLabs voice IDs for different styles
    ELEVENLABS_VOICES = {
        VoiceStyle.AGGRESSIVE: "onwK6e9ZLuTAKqWW03F9",  # Daniel - Deep, authoritative
        VoiceStyle.SMOOTH: "EXAVITQu4vr4xnSDxMaL",     # Bella - Smooth, engaging
        VoiceStyle.PROFESSIONAL: "pNInz6obpgDQGcFmaJgB"  # Adam - Professional, clear
    }

    # Azure voice names for different styles
    AZURE_VOICES = {
        VoiceStyle.AGGRESSIVE: "en-US-GuyNeural",
        VoiceStyle.SMOOTH: "en-US-JennyNeural",
        VoiceStyle.PROFESSIONAL: "en-US-DavisNeural"
    }

    # Google voice names for different styles
    GOOGLE_VOICES = {
        VoiceStyle.AGGRESSIVE: ("en-US-Neural2-D", "MALE"),
        VoiceStyle.SMOOTH: ("en-US-Neural2-F", "FEMALE"),
        VoiceStyle.PROFESSIONAL: ("en-US-Neural2-A", "MALE")
    }

    def __init__(
        self,
        provider: str = "auto",
        default_style: str = "aggressive"
    ):
        """
        Initialize voice generator

        Args:
            provider: TTS provider ('elevenlabs', 'azure', 'google', 'gtts', 'pyttsx3', 'auto')
            default_style: Default voice style
        """
        self.provider = self._select_provider(provider)
        self.default_style = VoiceStyle(default_style)
        self.client = None

        # Initialize selected provider
        self._initialize_provider()

        logger.info(f"Initialized VoiceGenerator with {self.provider.value} provider")

    def _select_provider(self, provider: str) -> VoiceProvider:
        """Select best available provider"""
        if provider.lower() != "auto":
            return VoiceProvider(provider.lower())

        # Auto-select best available provider
        if ELEVENLABS_AVAILABLE and os.getenv("ELEVENLABS_API_KEY"):
            return VoiceProvider.ELEVENLABS
        elif AZURE_AVAILABLE and os.getenv("AZURE_SPEECH_KEY"):
            return VoiceProvider.AZURE
        elif GOOGLE_AVAILABLE and os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            return VoiceProvider.GOOGLE
        elif GTTS_AVAILABLE:
            return VoiceProvider.GTTS
        elif PYTTSX3_AVAILABLE:
            return VoiceProvider.PYTTSX3
        else:
            raise RuntimeError("No TTS provider available. Install: pip install gtts")

    def _initialize_provider(self):
        """Initialize the selected provider"""
        try:
            if self.provider == VoiceProvider.ELEVENLABS:
                self._init_elevenlabs()
            elif self.provider == VoiceProvider.AZURE:
                self._init_azure()
            elif self.provider == VoiceProvider.GOOGLE:
                self._init_google()
            elif self.provider == VoiceProvider.GTTS:
                logger.info("gTTS ready (no initialization required)")
            elif self.provider == VoiceProvider.PYTTSX3:
                self._init_pyttsx3()
        except Exception as e:
            logger.error(f"Failed to initialize {self.provider.value}: {e}")
            # Fallback to gTTS
            if self.provider != VoiceProvider.GTTS and GTTS_AVAILABLE:
                logger.warning("Falling back to gTTS")
                self.provider = VoiceProvider.GTTS

    def _init_elevenlabs(self):
        """Initialize ElevenLabs API"""
        if not ELEVENLABS_AVAILABLE:
            raise ImportError("elevenlabs not installed. Run: pip install elevenlabs")

        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY not found in environment")

        self.client = ElevenLabs(api_key=api_key)
        logger.info("ElevenLabs API initialized")

    def _init_azure(self):
        """Initialize Azure Speech API"""
        if not AZURE_AVAILABLE:
            raise ImportError("azure-cognitiveservices-speech not installed")

        key = os.getenv("AZURE_SPEECH_KEY")
        region = os.getenv("AZURE_SPEECH_REGION", "eastus")

        if not key:
            raise ValueError("AZURE_SPEECH_KEY not found in environment")

        speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
        self.client = speech_config
        logger.info("Azure Speech API initialized")

    def _init_google(self):
        """Initialize Google Cloud TTS"""
        if not GOOGLE_AVAILABLE:
            raise ImportError("google-cloud-texttospeech not installed")

        self.client = texttospeech.TextToSpeechClient()
        logger.info("Google Cloud TTS initialized")

    def _init_pyttsx3(self):
        """Initialize pyttsx3 offline TTS"""
        if not PYTTSX3_AVAILABLE:
            raise ImportError("pyttsx3 not installed")

        self.client = pyttsx3.init()
        logger.info("pyttsx3 offline TTS initialized")

    def generate_voiceover(
        self,
        script: str,
        output_path: str,
        style: Optional[str] = None,
        voice_id: Optional[str] = None
    ) -> bool:
        """
        Generate voiceover from script

        Args:
            script: Script text to convert to speech
            output_path: Path to save audio file (MP3 or WAV)
            style: Voice style ('aggressive', 'smooth', 'professional')
            voice_id: Override voice ID for the provider (optional)

        Returns:
            True if successful, False otherwise
        """
        style_enum = VoiceStyle(style) if style else self.default_style

        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            logger.info(f"Generating voiceover with {self.provider.value} ({style_enum.value} style)")

            # Generate based on provider
            if self.provider == VoiceProvider.ELEVENLABS:
                success = self._generate_elevenlabs(script, output_path, style_enum, voice_id)
            elif self.provider == VoiceProvider.AZURE:
                success = self._generate_azure(script, output_path, style_enum, voice_id)
            elif self.provider == VoiceProvider.GOOGLE:
                success = self._generate_google(script, output_path, style_enum, voice_id)
            elif self.provider == VoiceProvider.GTTS:
                success = self._generate_gtts(script, output_path)
            elif self.provider == VoiceProvider.PYTTSX3:
                success = self._generate_pyttsx3(script, output_path, style_enum)
            else:
                logger.error(f"Unknown provider: {self.provider}")
                return False

            if success:
                logger.info(f"Voiceover saved to: {output_path}")
                return True
            else:
                logger.error("Voiceover generation failed")
                return False

        except Exception as e:
            logger.error(f"Failed to generate voiceover: {e}")
            return False

    def _generate_elevenlabs(
        self,
        script: str,
        output_path: Path,
        style: VoiceStyle,
        voice_id: Optional[str]
    ) -> bool:
        """Generate voiceover using ElevenLabs"""
        try:
            # Select voice
            selected_voice = voice_id or self.ELEVENLABS_VOICES.get(
                style,
                self.ELEVENLABS_VOICES[VoiceStyle.AGGRESSIVE]
            )

            # Voice settings for different styles
            if style == VoiceStyle.AGGRESSIVE:
                settings = VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.8,
                    use_speaker_boost=True
                )
            elif style == VoiceStyle.SMOOTH:
                settings = VoiceSettings(
                    stability=0.7,
                    similarity_boost=0.85,
                    style=0.6,
                    use_speaker_boost=True
                )
            else:  # PROFESSIONAL
                settings = VoiceSettings(
                    stability=0.65,
                    similarity_boost=0.8,
                    style=0.5,
                    use_speaker_boost=True
                )

            # Generate audio
            audio = self.client.generate(
                text=script,
                voice=selected_voice,
                voice_settings=settings,
                model="eleven_multilingual_v2"
            )

            # Save to file
            with open(output_path, 'wb') as f:
                for chunk in audio:
                    f.write(chunk)

            return True

        except Exception as e:
            logger.error(f"ElevenLabs generation failed: {e}")
            return False

    def _generate_azure(
        self,
        script: str,
        output_path: Path,
        style: VoiceStyle,
        voice_name: Optional[str]
    ) -> bool:
        """Generate voiceover using Azure TTS"""
        try:
            # Select voice
            selected_voice = voice_name or self.AZURE_VOICES.get(
                style,
                self.AZURE_VOICES[VoiceStyle.AGGRESSIVE]
            )

            # Configure audio output
            audio_config = speechsdk.audio.AudioOutputConfig(filename=str(output_path))

            # Create synthesizer
            self.client.speech_synthesis_voice_name = selected_voice
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.client,
                audio_config=audio_config
            )

            # Apply style-specific SSML
            ssml = self._build_azure_ssml(script, selected_voice, style)

            # Synthesize
            result = synthesizer.speak_ssml_async(ssml).get()

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return True
            else:
                logger.error(f"Azure synthesis failed: {result.reason}")
                return False

        except Exception as e:
            logger.error(f"Azure generation failed: {e}")
            return False

    def _build_azure_ssml(self, text: str, voice: str, style: VoiceStyle) -> str:
        """Build SSML for Azure with style controls"""
        # Style mappings
        prosody_rate = {
            VoiceStyle.AGGRESSIVE: "5%",
            VoiceStyle.SMOOTH: "-5%",
            VoiceStyle.PROFESSIONAL: "0%"
        }

        prosody_pitch = {
            VoiceStyle.AGGRESSIVE: "+5%",
            VoiceStyle.SMOOTH: "0%",
            VoiceStyle.PROFESSIONAL: "0%"
        }

        ssml = f"""
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
            <voice name='{voice}'>
                <prosody rate='{prosody_rate[style]}' pitch='{prosody_pitch[style]}'>
                    {text}
                </prosody>
            </voice>
        </speak>
        """
        return ssml

    def _generate_google(
        self,
        script: str,
        output_path: Path,
        style: VoiceStyle,
        voice_name: Optional[str]
    ) -> bool:
        """Generate voiceover using Google Cloud TTS"""
        try:
            # Select voice
            voice_info = self.GOOGLE_VOICES.get(style, self.GOOGLE_VOICES[VoiceStyle.AGGRESSIVE])

            if voice_name:
                # Custom voice name provided
                voice = texttospeech.VoiceSelectionParams(name=voice_name)
            else:
                voice = texttospeech.VoiceSelectionParams(
                    language_code="en-US",
                    name=voice_info[0],
                    ssml_gender=getattr(texttospeech.SsmlVoiceGender, voice_info[1])
                )

            # Configure audio
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.0 if style != VoiceStyle.AGGRESSIVE else 1.05,
                pitch=0.0 if style != VoiceStyle.AGGRESSIVE else 1.0
            )

            # Synthesize
            synthesis_input = texttospeech.SynthesisInput(text=script)
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )

            # Save to file
            with open(output_path, 'wb') as f:
                f.write(response.audio_content)

            return True

        except Exception as e:
            logger.error(f"Google TTS generation failed: {e}")
            return False

    def _generate_gtts(self, script: str, output_path: Path) -> bool:
        """Generate voiceover using gTTS (free, basic quality)"""
        import time
        
        if not GTTS_AVAILABLE:
            logger.warning("gtts not installed, trying pyttsx3 fallback")
            return self._generate_pyttsx3_fallback(script, output_path)
        
        max_retries = 2
        retry_delay = 3  # seconds
        
        for attempt in range(max_retries):
            try:
                # Generate speech
                tts = gTTS(text=script, lang='en', slow=False)
                tts.save(str(output_path))
                
                # Verify file is valid (not empty/corrupted)
                if output_path.exists() and output_path.stat().st_size > 1000:
                    return True
                else:
                    logger.warning("Generated file too small, may be corrupted")
                    raise Exception("Corrupted output")
                
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "Too Many Requests" in error_msg or "Corrupted" in error_msg:
                    if attempt < max_retries - 1:
                        logger.warning(f"gTTS failed, waiting {retry_delay}s before retry {attempt + 2}/{max_retries}")
                        time.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                    else:
                        # Fallback to pyttsx3
                        logger.warning("gTTS rate limited, falling back to pyttsx3 (offline)")
                        return self._generate_pyttsx3_fallback(script, output_path)
                
                logger.error(f"gTTS generation failed: {e}")
                # Try pyttsx3 fallback
                return self._generate_pyttsx3_fallback(script, output_path)
        
        return self._generate_pyttsx3_fallback(script, output_path)
    
    def _generate_pyttsx3_fallback(self, script: str, output_path: Path) -> bool:
        """Fallback TTS using pyttsx3 (offline, no rate limits)"""
        try:
            import pyttsx3
            
            logger.info("Using pyttsx3 offline TTS...")
            engine = pyttsx3.init()
            
            # Configure voice
            engine.setProperty('rate', 170)  # Speed
            engine.setProperty('volume', 1.0)
            
            # Try to use a better voice if available
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'david' in voice.name.lower() or 'male' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
            
            # Save to file
            engine.save_to_file(script, str(output_path))
            engine.runAndWait()
            
            # Verify file exists and has content
            if output_path.exists() and output_path.stat().st_size > 100:
                logger.info("pyttsx3 voiceover generated successfully")
                return True
            else:
                logger.error("pyttsx3 failed to generate audio file")
                return False
                
        except Exception as e:
            logger.error(f"pyttsx3 fallback failed: {e}")
            return False

    def _generate_pyttsx3(
        self,
        script: str,
        output_path: Path,
        style: VoiceStyle
    ) -> bool:
        """Generate voiceover using pyttsx3 (offline)"""
        try:
            # Configure voice properties based on style
            if style == VoiceStyle.AGGRESSIVE:
                self.client.setProperty('rate', 180)  # Faster
                self.client.setProperty('volume', 1.0)
            elif style == VoiceStyle.SMOOTH:
                self.client.setProperty('rate', 150)  # Slower
                self.client.setProperty('volume', 0.9)
            else:  # PROFESSIONAL
                self.client.setProperty('rate', 165)  # Normal
                self.client.setProperty('volume', 0.95)

            # Save to file
            self.client.save_to_file(script, str(output_path))
            self.client.runAndWait()

            return True

        except Exception as e:
            logger.error(f"pyttsx3 generation failed: {e}")
            return False

    def generate_from_script_file(
        self,
        script_path: str,
        output_path: str,
        style: Optional[str] = None
    ) -> bool:
        """
        Generate voiceover from script file

        Args:
            script_path: Path to script text file
            output_path: Path to save audio file
            style: Voice style (optional)

        Returns:
            True if successful
        """
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                script = f.read().strip()

            return self.generate_voiceover(script, output_path, style)

        except Exception as e:
            logger.error(f"Failed to read script file: {e}")
            return False

    def get_audio_duration(self, audio_path: str) -> Optional[float]:
        """
        Get duration of audio file in seconds

        Args:
            audio_path: Path to audio file

        Returns:
            Duration in seconds, or None if failed
        """
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(audio_path)
            return len(audio) / 1000.0  # Convert ms to seconds
        except Exception as e:
            logger.warning(f"Could not determine audio duration: {e}")
            return None


# Example usage
if __name__ == "__main__":
    # Test voice generator
    generator = VoiceGenerator(provider="auto", default_style="aggressive")

    # Sample script
    test_script = """Born to dominate.

2024 Low Rider ST. Milwaukee-Eight 117 engine delivering pure power. 
Sport-tuned suspension. Touring-ready with aggressive style.

Barely broken in at just 377 miles. Yours for twenty-seven thousand, nine ninety.

Don't wait. Scan to reserve. Available now at San Diego Harley-Davidson."""

    # Generate voiceover
    output_path = "./test_voiceover.mp3"
    success = generator.generate_voiceover(
        script=test_script,
        output_path=output_path,
        style="aggressive"
    )

    if success:
        print(f"\nVoiceover generated successfully!")
        print(f"Saved to: {output_path}")

        # Get duration
        duration = generator.get_audio_duration(output_path)
        if duration:
            print(f"Duration: {duration:.2f} seconds")
    else:
        print("\nVoiceover generation failed")


