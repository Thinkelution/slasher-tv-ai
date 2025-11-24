General Idea:
The Slasher Sale TV Channel is a nonstop, 24/7 stream of Harley-Davidson bikes pulled straight from dealer inventory.
Every few minutes, a new bike appears — price, photos, and dealer branding — like a live shopping channel for motorcycles.

How It Works
Live Dealer Feeds
Each dealer already keeps an online feed showing what’s in stock — model, year, price, and photos.
We automatically collect those feeds across all participating dealerships.
Instant Video Creation
The system turns every listing into a short promo clip:
Bike spins, price slashes, music kicks in, and the dealer’s logo pops up.
When the bike sells or the price changes, the video updates automatically.


Workflow
Feed ingestion: Python job (scheduled on the server pulls XML/JSON or scrapes pages.
Normalization: Clean and store as JSON lines per dealer.
Media download: Download all listing images to /assets/{dealer}/{sku}/.



Phase 2 — AI Generation (DGX Spark or GPU Server)
The NVIDIA DGX Spark (or a GPU server) runs all AI workloads locally:
Script writing: Short, ad-style copy for each vehicle (e.g. “Own the road. 2023 Road Glide ST — 117 cubic inches of Harley power.”).
Voiceover generation: AI TTS (Dan’s or a dealer voice).
Image cleanup: Remove backgrounds, upscale, standardize aspect ratios.
Video layout logic: Decide placement (hero image, dealer logo, offer text, etc.).
Optional: generate captions, hashtags, or CTA text.


Immediate Requirement: 
Sample data feed for inventory. It is my vision to take this and make 30 second videos. Taking the photos and and making the videos. I finally got the sample feeds. Here we want to automate the professional creation of little commercials that make it out to a live playout channel.

This is how the inventory is online https://sandiegoharley.com/used-inventory