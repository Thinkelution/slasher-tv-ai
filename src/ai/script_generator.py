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

# Number to words conversion for TTS
NUM_WORDS = {
    0: 'zero', 1: 'one', 2: 'two', 3: 'three', 4: 'four',
    5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine',
    10: 'ten', 11: 'eleven', 12: 'twelve', 13: 'thirteen',
    14: 'fourteen', 15: 'fifteen', 16: 'sixteen', 17: 'seventeen',
    18: 'eighteen', 19: 'nineteen', 20: 'twenty', 30: 'thirty',
    40: 'forty', 50: 'fifty', 60: 'sixty', 70: 'seventy',
    80: 'eighty', 90: 'ninety'
}

def number_to_words(n: int) -> str:
    """Convert a number to words for TTS-friendly output"""
    if n < 0:
        return 'negative ' + number_to_words(-n)
    if n < 20:
        return NUM_WORDS[n]
    if n < 100:
        tens, unit = divmod(n, 10)
        return NUM_WORDS[tens * 10] + ('' if unit == 0 else ' ' + NUM_WORDS[unit])
    if n < 1000:
        hundreds, remainder = divmod(n, 100)
        return NUM_WORDS[hundreds] + ' hundred' + ('' if remainder == 0 else ' ' + number_to_words(remainder))
    if n < 10000:
        thousands, remainder = divmod(n, 1000)
        return number_to_words(thousands) + ' thousand' + ('' if remainder == 0 else ' ' + number_to_words(remainder))
    if n < 1000000:
        thousands, remainder = divmod(n, 1000)
        return number_to_words(thousands) + ' thousand' + ('' if remainder == 0 else ' ' + number_to_words(remainder))
    return str(n)  # Fallback for very large numbers

def convert_numbers_in_text(text: str) -> str:
    """Convert all numbers in text to words for better TTS"""
    import re
    
    # Convert prices like $19,999 or $6,999
    def replace_price(match):
        price_str = match.group(0).replace('$', '').replace(',', '')
        try:
            price = int(float(price_str))
            return number_to_words(price) + ' dollars'
        except:
            return match.group(0)
    
    text = re.sub(r'\$[\d,]+', replace_price, text)
    
    # Convert years like 2024
    def replace_year(match):
        year = int(match.group(0))
        if 2000 <= year <= 2099:
            return 'twenty ' + number_to_words(year - 2000).replace('zero', 'twenty')
        elif 1900 <= year <= 1999:
            return 'nineteen ' + number_to_words(year - 1900)
        return match.group(0)
    
    text = re.sub(r'\b(19|20)\d{2}\b', replace_year, text)
    
    # Convert standalone numbers
    def replace_number(match):
        try:
            num = int(match.group(0).replace(',', ''))
            return number_to_words(num)
        except:
            return match.group(0)
    
    text = re.sub(r'\b\d{1,3}(?:,\d{3})*\b', replace_number, text)
    text = re.sub(r'\b\d+\b', replace_number, text)
    
    return text


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

        # Convert any remaining numbers to words for better TTS
        script = convert_numbers_in_text(script)
        
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

        # Style guidance - Enthusiastic Salesman Voice
        style_guide = {
            "aggressive": "ENTHUSIASTIC CAR SALESMAN who's genuinely EXCITED about this deal. High energy, passionate, like you can't WAIT to tell them about this bike. Think local dealership TV commercial where the owner is pumped up.",
            "smooth": "CONFIDENT SALESMAN who knows this is a premium product. Smooth, persuasive, like a luxury car salesman who lets the product speak for itself.",
            "professional": "TRUSTWORTHY DEALER who wants to help you find your dream bike. Warm, genuine, like talking to a friend who happens to sell motorcycles."
        }.get(style, "Enthusiastic and genuine")

        # Include description snippet if available
        desc_snippet = ""
        if description:
            # Extract key selling points from description
            desc_snippet = f"\n\nKey Details (use as inspiration):\n{description[:400]}"

        prompt = f"""You are an ENTHUSIASTIC MOTORCYCLE SALESMAN recording a 30-second TV/radio commercial.

You LOVE this bike and you're EXCITED to tell people about this amazing deal!

MOTORCYCLE YOU'RE SELLING:
• {year} {make} {model}
• Price: ${price:,.0f}
• {details_text}
{desc_snippet}

TIMING: Exactly {TARGET_WORD_COUNT} words ({MIN_WORD_COUNT}-{MAX_WORD_COUNT} range) = 30 seconds when spoken

YOUR PERSONALITY: {style_guide}

HOW A REAL SALESMAN TALKS:
1. EXCITED and GENUINE - you actually love motorcycles
2. PERSONAL - use "you", "your", talk directly to the viewer
3. URGENT but not pushy - this is a great opportunity they shouldn't miss
4. CONFIDENT - you know this is an amazing bike at a great price
5. NATURAL flow - not robotic, like you're talking to a friend
6. HIGHLIGHT THE VALUE - make them feel they're getting a steal

SCRIPT FLOW:
- HOOK: Grab attention with something exciting
- THE BIKE: What makes this bike special (2-3 key points)
- THE DEAL: Price reveal - make it sound like an incredible value
- THE CLOSE: Create urgency, tell them to act now
- TAG: Always end with "Scan to reserve. San Diego Harley-Davidson."

IMPORTANT RULES:
- ALWAYS write ALL numbers as WORDS - the voice struggles with digits:
  • Years: "twenty twenty-four" NOT "2024"
  • Prices: "six thousand nine hundred ninety-nine dollars" NOT "$6,999"
  • Mileage: "eight hundred miles" NOT "800 miles"
  • Engine: "one seventeen" NOT "117"
  • NEVER use digits 0-9 anywhere in the script
- NO robotic pauses or weird formatting
- NO questions - confident statements only
- Sound like a REAL PERSON, not AI
- Be ENTHUSIASTIC without being cheesy

EXAMPLE SALESMAN SCRIPTS:

Example 1 (High Energy):
"Ladies and gentlemen, feast your eyes on this beauty! The twenty twenty-four Harley-Davidson Low Rider ST. We're talking Milwaukee-Eight one seventeen power, that unmistakable Harley rumble, and styling that turns heads everywhere you go. And here's the best part - we've got this incredible machine priced at just twenty-two thousand four ninety-nine. At this price, it's not gonna last. Get down here today. Scan to reserve. San Diego Harley-Davidson."

Example 2 (Confident):
"Now this is what I'm talking about. A twenty twenty-three Street Glide in pristine condition, only eight hundred miles on the clock. Somebody barely broke her in and now she's yours for the taking. Full touring setup, premium sound, ready to eat up the highway. We're letting her go for eighteen thousand nine ninety-nine. Trust me, deals like this don't come around often. Scan to reserve. San Diego Harley-Davidson."

NOW WRITE YOUR SCRIPT (just the voiceover text, nothing else):"""

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
