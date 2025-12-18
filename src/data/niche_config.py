"""Niche configuration for Reddit trend ingestion.

Maps each niche to relevant subreddits and keywords for filtering.
"""

NICHES = {
    "Tech/Gaming": {
        "subreddits": ["gaming", "pcgaming", "Games", "truegaming", "Android", "apple"],
        "keywords": ["game", "gaming", "play", "console", "PC", "mobile", "iPhone", "Android", "app", "tech", "AI", "VR", "AR", "software", "hardware", "device", "gadget"]
    },
    "Fashion/Beauty": {
        "subreddits": ["fashion", "streetwear", "malefashionadvice", "femalefashionadvice", "MakeupAddiction", "SkincareAddiction"],
        "keywords": ["fashion", "style", "outfit", "wear", "clothes", "dress", "beauty", "makeup", "skincare", "hair", "nails", "cosmetic"]
    },
    "Finance/Crypto": {
        "subreddits": ["CryptoCurrency", "Bitcoin", "stocks", "investing", "wallstreetbets", "StockMarket"],
        "keywords": ["crypto", "bitcoin", "ethereum", "stock", "invest", "trading", "market", "price", "portfolio", "finance", "money", "dollar"]
    },
    "Health/Fitness": {
        "subreddits": ["fitness", "loseit", "bodyweightfitness", "xxfitness", "weightroom", "running"],
        "keywords": ["fitness", "workout", "exercise", "gym", "weight", "diet", "health", "nutrition", "muscle", "cardio", "running", "training"]
    },
    "Food/Cooking": {
        "subreddits": ["Cooking", "recipes", "AskCulinary", "food", "52weeksofcooking", "EatCheapAndHealthy"],
        "keywords": ["recipe", "cook", "bake", "food", "meal", "dish", "ingredient", "kitchen", "chef", "restaurant", "eat"]
    },
    "Travel": {
        "subreddits": ["travel", "solotravel", "TravelHacks", "digitalnomad", "backpacking", "Shoestring"],
        "keywords": ["travel", "trip", "vacation", "destination", "flight", "hotel", "tour", "visit", "abroad", "country", "city"]
    },
    "Entertainment/Media": {
        "subreddits": ["movies", "television", "TrueFilm", "netflix", "Music", "hiphopheads"],
        "keywords": ["movie", "film", "show", "series", "TV", "watch", "streaming", "Netflix", "music", "song", "album", "artist", "band"]
    },
    "Business/Marketing": {
        "subreddits": ["Entrepreneur", "startups", "smallbusiness", "marketing", "digital_marketing", "ecommerce"],
        "keywords": ["business", "startup", "entrepreneur", "marketing", "brand", "customer", "sales", "revenue", "growth", "SEO", "social media"]
    },
    "Lifestyle/Vlogs": {
        "subreddits": ["productivity", "GetMotivated", "selfimprovement", "DecidingToBeBetter", "minimalism", "organization"],
        "keywords": ["lifestyle", "routine", "habit", "productivity", "organize", "motivate", "improve", "minimalism", "declutter", "life"]
    },
    "Celebrities/Pop Culture": {
        "subreddits": ["popculture", "Deuxmoi", "entertainment", "Fauxmoi", "celebs", "popculturechat"],
        "keywords": ["celebrity", "celeb", "star", "famous", "actor", "actress", "singer", "pop culture", "gossip", "drama", "award"]
    },
    "Faith/Religion": {
        "subreddits": ["Christianity", "TrueChristian", "religion", "spirituality", "Buddhism", "OpenChristian"],
        "keywords": ["faith", "religion", "spiritual", "god", "church", "prayer", "bible", "christian", "buddhist", "belief"]
    }
}


def get_subreddits_for_niche(niche: str) -> list[str]:
    """Return list of subreddits for a given niche."""
    return NICHES.get(niche, {}).get("subreddits", [])


def get_keywords_for_niche(niche: str) -> list[str]:
    """Return search keywords for a given niche."""
    return NICHES.get(niche, {}).get("keywords", [])


def get_all_niches() -> list[str]:
    """Return all available niche names."""
    return list(NICHES.keys())
