"""
AI Script Generator for motorcycle promo videos
Professional 30-second TV commercial scripts optimized for voiceover
"""

import os
from typing import Optional
import logging
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for 30-second voiceover timing
# Average speaking rate: 150 words per minute = 2.5 words per second
# 30 seconds = 75 words (comfortable pace for TV commercial)
TARGET_WORD_COUNT = 75
MIN_WORD_COUNT = 70
MAX_WORD_COUNT = 85


class ScriptGenerator:
    """Generate AI-powered ad scripts for motorcycle videos - optimized for 30-second voiceover"""

    def __init__(
        self,
        provider: str = "openai",
        model: Optional[str] = None
    ):
        """
        Initialize script generator

        Args:
            provider: AI provider ('openai' or 'anthropic')
            model: Model name (optional, uses defaults)
        """
        self.provider = provider.lower()

        # Initialize API clients
        if self.provider == "openai":
            if OpenAI is None:
                raise ImportError("openai package not installed. Run: pip install openai")
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model = model or os.getenv("SCRIPT_MODEL", "gpt-4o")
        elif self.provider == "anthropic":
            if Anthropic is None:
                raise ImportError("anthropic package not installed. Run: pip install anthropic")
            self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            self.model = model or "claude-3-5-sonnet-20241022"
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        logger.info(f"Initialized ScriptGenerator with {self.provider} ({self.model})")

    def generate_script(
        self,
        year: int,
        make: str,
        model: str,
        price: float,
        description: Optional[str] = None,
        color: Optional[str] = None,
        mileage: Optional[int] = None,
        engine: Optional[str] = None,
        is_custom: bool = False,
        style: str = "aggressive"
    ) -> str:
        """
        Generate 30-second promo script

        Args:
            year: Model year
            make: Manufacturer
            model: Model name
            price: Price
            description: Listing description (optional)
            color: Color (optional)
            mileage: Mileage (optional)
            engine: Engine specs (optional)
            is_custom: Whether bike is custom
            style: Script style ('aggressive', 'smooth', 'professional')

        Returns:
            Generated script text
        """
        # Build prompt
        prompt = self._build_prompt(
            year=year,
            make=make,
            model=model,
            price=price,
            description=description,
            color=color,
            mileage=mileage,
            engine=engine,
            is_custom=is_custom,
            style=style
        )

        # Generate script using chosen provider
        if self.provider == "openai":
            script = self._generate_openai(prompt)
        elif self.provider == "anthropic":
            script = self._generate_anthropic(prompt)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

        logger.info(f"Generated script for {year} {make} {model}")
        return script

    def _build_prompt(
        self,
        year: int,
        make: str,
        model: str,
        price: float,
        description: Optional[str],
        color: Optional[str],
        mileage: Optional[int],
        engine: Optional[str],
        is_custom: bool,
        style: str
    ) -> str:
        """Build prompt for AI model - optimized for professional 30-second voiceover"""

        # Prepare bike details
        details = []
        if color:
            details.append(f"Color: {color}")
        if mileage is not None:
            if mileage < 5000:
                details.append(f"Only {mileage:,} miles")
            else:
                details.append(f"Mileage: {mileage:,}")
        if engine:
            details.append(f"Engine: {engine}")
        if is_custom:
            details.append("Custom build")

        details_text = " | ".join(details) if details else "Premium condition"

        # Style guidance for bold TV commercial voice
        style_guide = {
            "aggressive": "BOLD, POWERFUL, COMMANDING. Short punchy sentences. Deep authoritative tone. Think monster truck rally announcer meets luxury car commercial.",
            "smooth": "SOPHISTICATED, CONFIDENT, PREMIUM. Flowing elegant sentences. Think luxury automotive brand with prestige.",
            "professional": "TRUSTWORTHY, AUTHORITATIVE, COMPELLING. Clear direct sentences. Think premium dealership commercial."
        }.get(style, "Bold and commanding")

        # Include description snippet if available
        desc_snippet = ""
        if description:
            # Extract key selling points from description
            desc_snippet = f"\n\nKey Details (use as inspiration):\n{description[:400]}"

        prompt = f"""You are writing a professional 30-SECOND TV COMMERCIAL SCRIPT for a bold male voiceover artist.

MOTORCYCLE:
• {year} {make} {model}
• Price: ${price:,.0f}
• {details_text}
{desc_snippet}

CRITICAL TIMING REQUIREMENTS:
- EXACTLY {TARGET_WORD_COUNT} words (range: {MIN_WORD_COUNT}-{MAX_WORD_COUNT})
- Speaking rate: 2.5 words/second for bold dramatic delivery
- Total duration: 30 seconds when spoken

SCRIPT STRUCTURE (30 seconds total):
[0-3 sec] HOOK: One powerful opening line that grabs attention
[3-12 sec] FEATURES: 2-3 compelling benefits/features with emotional impact  
[12-20 sec] THE OFFER: Price reveal with urgency and value proposition
[20-27 sec] CALL TO ACTION: Create urgency, drive action
[27-30 sec] TAG: "Scan to reserve. San Diego Harley-Davidson."

VOICE STYLE: {style_guide}

RULES:
1. Write for a DEEP, BOLD, AUTHORITATIVE male voice
2. Use SHORT, PUNCHY sentences that punch hard
3. Include DRAMATIC PAUSES (marked with periods)
4. NO questions - only powerful statements
5. NO filler words (um, uh, well, so)
6. Numbers spoken as words ("six thousand nine hundred ninety-nine dollars")
7. Focus on EMOTION and LIFESTYLE over specs
8. Create URGENCY without being cheesy
9. End EXACTLY with: "Scan to reserve. San Diego Harley-Davidson."

EXAMPLE PROFESSIONAL SCRIPTS:

Example 1 (Aggressive - 78 words):
"Dominance. Redefined. The {year} {make}. Raw American muscle wrapped in chrome and attitude. A thundering engine that announces your arrival before you're even seen. Custom styling that turns every street into your personal runway. Now. Just ${price:,.0f}. This isn't just a motorcycle. It's a statement. And statements like this don't last. Scan to reserve. San Diego Harley-Davidson."

Example 2 (Smooth - 76 words):
"Some machines are built to ride. This one. Is built to be remembered. The {year} {make}. Precision engineering meets timeless American craftsmanship. Every curve. Every detail. Designed for those who refuse to blend in. Priced at ${price:,.0f}. Excellence. Within reach. Your next chapter starts now. Scan to reserve. San Diego Harley-Davidson."

NOW WRITE THE SCRIPT (just the voiceover text, nothing else):"""

        return prompt

    def _generate_openai(self, prompt: str) -> str:
        """Generate script using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert TV commercial copywriter specializing in motorcycle advertising. You write punchy, emotional, compelling scripts that sell."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                max_tokens=300
            )

            script = response.choices[0].message.content.strip()
            return script

        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return self._fallback_script(prompt)

    def _generate_anthropic(self, prompt: str) -> str:
        """Generate script using Anthropic Claude"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                temperature=0.8,
                system="You are an expert TV commercial copywriter specializing in motorcycle advertising. You write punchy, emotional, compelling scripts that sell.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            script = response.content[0].text.strip()
            return script

        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            return self._fallback_script(prompt)

    def _fallback_script(self, prompt: str) -> str:
        """Generate fallback script if AI fails - professional 30-second template"""
        logger.warning("Using fallback script template")
        return """Power. Unleashed.

This is the machine that changes everything. Raw American engineering. Thundering performance. Unmistakable presence on every road you conquer.

A legend. Built for those who lead. Not follow.

Available now at an unbeatable price. This opportunity won't wait. And neither should you.

Scan to reserve. San Diego Harley-Davidson."""

    def _validate_word_count(self, script: str) -> bool:
        """Validate script is within target word count for 30-second delivery"""
        word_count = len(script.split())
        is_valid = MIN_WORD_COUNT <= word_count <= MAX_WORD_COUNT
        if not is_valid:
            logger.warning(f"Script word count {word_count} outside target range ({MIN_WORD_COUNT}-{MAX_WORD_COUNT})")
        return is_valid

    def get_script_duration_estimate(self, script: str) -> float:
        """Estimate script duration in seconds (2.5 words/second for dramatic delivery)"""
        word_count = len(script.split())
        return word_count / 2.5


# Example usage
if __name__ == "__main__":
    # Test with OpenAI
    generator = ScriptGenerator(provider="openai")

    script = generator.generate_script(
        year=2024,
        make="Harley-Davidson",
        model="Low Rider ST",
        price=27990,
        color="Billiard Gray",
        mileage=377,
        engine="Milwaukee-Eight 117",
        is_custom=False,
        style="aggressive"
    )

    print("\nGenerated Script:")
    print("=" * 50)
    print(script)
    print("=" * 50)
