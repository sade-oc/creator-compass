# Niche configuration for trend categorisation.
# Maps each content creator niche to relevant keywords for Twitter trend classification.
# Used for rule-based NLP categorisation of trending topics into creator-relevant domains.

NICHES = {
    "Tech/Gaming": {
        "keywords": ["game", "gaming", "play", "console", "PC", "mobile", "iPhone", "Android", "app", "tech", "AI", "VR", "AR", "software", "hardware", "device", "gadget"]
    },
    "Fashion/Beauty": {
        "keywords": ["fashion", "style", "outfit", "wear", "clothes", "dress", "beauty", "makeup", "skincare", "hair", "nails", "cosmetic"]
    },
    "Finance/Crypto": {
        "keywords": ["crypto", "bitcoin", "ethereum", "stock", "invest", "trading", "market", "price", "portfolio", "finance", "money", "dollar"]
    },
    "Health/Fitness": {
        "keywords": ["fitness", "workout", "exercise", "gym", "weight", "diet", "health", "nutrition", "muscle", "cardio", "running", "training"]
    },
    "Food/Cooking": {
        "keywords": ["recipe", "cook", "bake", "food", "meal", "dish", "ingredient", "kitchen", "chef", "restaurant", "eat"]
    },
    "Travel": {
        "keywords": ["travel", "trip", "vacation", "destination", "flight", "hotel", "tour", "visit", "abroad", "country", "city"]
    },
    "Entertainment/Media": {
        "keywords": ["movie", "film", "show", "series", "TV", "watch", "streaming", "Netflix", "music", "song", "album", "artist", "band"]
    },
    "Business/Marketing": {
        "keywords": ["business", "startup", "entrepreneur", "marketing", "brand", "customer", "sales", "revenue", "growth", "SEO", "social media"]
    },
    "Lifestyle/Vlogs": {
        "keywords": ["lifestyle", "routine", "habit", "productivity", "organise", "motivate", "improve", "minimalism", "declutter", "life"]
    },
    "Celebrities/Pop Culture": {
        "keywords": ["celebrity", "celeb", "star", "famous", "actor", "actress", "singer", "pop culture", "gossip", "drama", "award"]
    },
    "Sports": {
        "keywords": ["sports", "nfl", "nba", "mlb", "nhl", "soccer", "football", "basketball", "baseball", "hockey", "athlete", "player", "team", "game", "match", "bowl", "playoffs", "championship", "finals", "league", "coach", "ufc", "mma", "fighting"]
    },
    "Politics/News": {
        "keywords": ["politics", "political", "election", "vote", "senate", "congress", "president", "governor", "bill", "law", "policy", "government", "democrat", "republican", "campaign", "legislation"]
    },
    "Faith/Religion": {
        "keywords": ["faith", "religion", "spiritual", "god", "church", "prayer", "bible", "christian", "buddhist", "belief"]
    }
}




def get_keywords_for_niche(niche: str) -> list[str]:
    """Return search keywords for a given niche."""
    return NICHES.get(niche, {}).get("keywords", [])


def get_all_niches() -> list[str]:
    """
    Return all available content creator niche names.
    
    Returns:
        List of 13 niche categories used for trend classification
    """
    return list(NICHES.keys())
