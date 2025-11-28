"""
AI Script Generator for motorcycle promo videos
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


class ScriptGenerator:
    """Generate AI-powered ad scripts for motorcycle videos"""

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
            self.model = model or os.getenv("SCRIPT_MODEL", "gpt-4")
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
        """Build prompt for AI model"""

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

        details_text = " | ".join(details) if details else "No additional details"

        # Style guidance
        style_guide = {
            "aggressive": "High-energy, bold, commanding. Use short punchy sentences. Emphasize power and attitude.",
            "smooth": "Smooth, sophisticated, elegant. Use flowing sentences. Emphasize style and craftsmanship.",
            "professional": "Clear, informative, trustworthy. Use balanced sentences. Emphasize value and reliability."
        }.get(style, "Balanced and engaging")

        # Include description snippet if available
        desc_snippet = ""
        if description:
            desc_snippet = f"\n\nListing Description (use as inspiration, don't copy verbatim):\n{description[:500]}"

        prompt = f"""Write a 30-second TV commercial voiceover script for this motorcycle:

BIKE: {year} {make} {model}
PRICE: ${price:,.0f}
DETAILS: {details_text}

STRICT REQUIREMENTS:
1. EXACTLY 70-80 words total (this is critical for 30-second timing)
2. Style: {style_guide}
3. Structure:
   - Opening hook: 1 punchy sentence (5-8 words)
   - Features: 2-3 short sentences about the bike (25-30 words)
   - Price: 1 sentence with price mention (10-12 words)
   - CTA: End with "Scan to reserve now. San Diego Harley-Davidson." (8 words)

4. NO questions, NO filler words
5. Short punchy sentences only
6. Focus on emotion and power

Write ONLY the script (70-80 words), nothing else:"""

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
        """Generate fallback script if AI fails"""
        logger.warning("Using fallback script template")
        return """The road is calling. This is your answer.

A stunning Harley-Davidson ready to dominate every mile. Powerful engine. Legendary craftsmanship. Unmistakable style.

And right now, it's yours for an unbeatable price.

Don't wait. This deal won't last. Scan to reserve. Available now at San Diego Harley-Davidson."""


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
