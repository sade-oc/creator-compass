#Content ideation pipeline - AI-powered short-form video idea generation.

import os
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Literal
from openai import OpenAI

Platform = Literal["TikTok", "Instagram Reels", "YouTube Shorts"]


def build_system_prompt() -> str:
    # Build the system prompt defining AI's role.
    return """You are an expert short-form video content strategist specializing in TikTok, Instagram Reels, and YouTube Shorts. You help content creators generate viral-worthy video ideas based on trending topics. Your ideas are:
- Creative and unique
- Actionable with specific filming directions
- Optimised for engagement
- Platform-appropriate for short-form video (15-60 seconds)"""


def build_platform_instructions(platform: Platform) -> str:
    # Get platform-specific optimization instructions.
    instructions = {
        "TikTok": """Optimise for TikTok's FYP algorithm. Focus on:
- Fast-paced editing with quick cuts
- Trending sounds/music integration
- Text overlays for accessibility
- Hooks in first 1-2 seconds (critical for FYP)
- Comment-bait elements to drive engagement""",
        
        "Instagram Reels": """Optimise for Instagram Reels. Focus on:
- Aesthetic visuals and polished production
- Smooth transitions and effects
- Instagram-native features (stickers, filters)
- Relatable storytelling
- Strong first frame (thumbnail matters for discover page)""",
        
        "YouTube Shorts": """Optimise for YouTube Shorts. Focus on:
- Educational or entertaining value
- Clear narrative arc with beginning/middle/end
- YouTube audience preferences (slightly older demographic)
- Strong CTAs for subscribe/like
- Slightly longer form (30-60 sec works better than 15-30)"""
    }
    return instructions.get(platform, "")


def build_user_prompt(
    trend_topic: str,
    niche: str,
    platform: Platform,
    keywords: list[str],
    hashtags: list[str],
    sentiment: str,
    num_variations: int
) -> str:
    # Build the main user prompt with trend context.
    
    keywords_str = ", ".join(keywords[:10]) if keywords else "None"
    hashtags_str = ", ".join(hashtags[:10]) if hashtags else "None"
    platform_instructions = build_platform_instructions(platform)
    
    prompt = f"""Generate {num_variations} creative short-form video content ideas based on this trending topic.

TREND CONTEXT:
Topic: {trend_topic}
Niche: {niche}
Platform: {platform}
Top Keywords: {keywords_str}
Popular Hashtags: {hashtags_str}
Sentiment: {sentiment}

{platform_instructions}

For EACH idea, provide:
1. Title (catchy, max 60 characters)
2. Hook (attention-grabbing opening line for first 3 seconds)
3. Angle (unique perspective or approach to the trend)
4. Description (100-200 words explaining the full video concept)
5. Visual Style (e.g., POV, Tutorial, Storytime, Transition, Before/After, Reaction)
6. Duration (either "15-30 sec" or "30-60 sec")
7. Suggested Shots (array of 3-5 specific scenes/clips to film)
8. Caption (engaging caption with call-to-action)
9. Hashtags (array of 5-10 relevant hashtags for discoverability)
10. Estimated Engagement ("High", "Medium", or "Low")
11. Engagement Reasoning (brief explanation of why this engagement level)

REQUIREMENTS:
- Ideas must be DISTINCT from each other (different angles, not variations)
- Focus on {niche} audience specifically
- Make it actionable - creators should know exactly what to film
- Include trending elements from the topic
- Consider the {sentiment} sentiment in your creative approach
- Be specific about shots and execution

Return ONLY a JSON object (not an array) with this exact structure:
{{
  "ideas": [
    {{
      "title": "string (max 60 chars)",
      "hook": "string",
      "angle": "string",
      "description": "string (100-200 words)",
      "visual_style": "string",
      "duration": "15-30 sec" or "30-60 sec",
      "suggested_shots": ["string", "string", "string"],
      "caption": "string",
      "hashtags": ["#string", "#string"],
      "estimated_engagement": "High" or "Medium" or "Low",
      "engagement_reasoning": "string"
    }}
  ]
}}"""
    
    return prompt


def generate_content_ideas(
    trend_topic: str,
    niche: str,
    platform: Platform = "TikTok",
    keywords: list[str] | None = None,
    hashtags: list[str] | None = None,
    sentiment: str = "neutral",
    num_variations: int = 3
) -> dict[str, Any]:
    """Generate AI-powered content ideas for a trending topic.
    
    Args:
        trend_topic: The trending topic to generate ideas about
        niche: Content creator's niche (e.g., "Entertainment/Media", "Tech/Gaming")
        platform: Target platform (TikTok, Instagram Reels, YouTube Shorts)
        keywords: Top keywords from trend analysis
        hashtags: Popular hashtags from trend analysis
        sentiment: Average sentiment (positive/neutral/negative)
        num_variations: Number of distinct ideas to generate (default: 3)
        
    Returns:
        Dict containing:
        - success: bool
        - ideas: list of generated content ideas
        - trend_topic: source trend
        - total_generated: count
        - generation_time: seconds
        - error: error message (if success=False)
    """
    
    start_time = time.time()
    
    # Defaults
    keywords = keywords or []
    hashtags = hashtags or []
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "success": False,
            "error": "OPENAI_API_KEY not found in environment",
            "ideas": [],
            "trend_topic": trend_topic,
            "total_generated": 0,
            "generation_time": 0
        }
    
    try:
        # Build prompts
        system_prompt = build_system_prompt()
        user_prompt = build_user_prompt(
            trend_topic, niche, platform, keywords, 
            hashtags, sentiment, num_variations
        )
        
        print(f"\n🎬 Generating {num_variations} content ideas for: {trend_topic}")
        print(f"   Platform: {platform} | Niche: {niche}")
        
        # Call OpenAI API
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Fast and cost-effective
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.85,  # Higher creativity for ideation
            max_tokens=3000,
            response_format={"type": "json_object"}  # Ensures JSON response
        )
        
        # Parse response
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from OpenAI")
        
        parsed = json.loads(content)
        ideas = parsed.get("ideas", [])
        
        if not ideas:
            raise ValueError("No ideas generated in response")
        
        # Add metadata to each idea
        enriched_ideas = []
        for idea in ideas:
            idea["idea_id"] = str(uuid.uuid4())
            idea["trend_topic"] = trend_topic
            idea["niche"] = niche
            idea["platform"] = platform
            idea["generated_at"] = datetime.now(timezone.utc).isoformat()
            
            # Calculate confidence score (0.0-1.0) based on engagement
            engagement_level = idea.get("estimated_engagement", "Medium")
            confidence_map = {"High": 0.85, "Medium": 0.70, "Low": 0.55}
            idea["confidence_score"] = confidence_map.get(engagement_level, 0.70)
            
            enriched_ideas.append(idea)
        
        generation_time = round(time.time() - start_time, 2)
        
        print(f"   ✓ Generated {len(enriched_ideas)} ideas in {generation_time}s")
        
        return {
            "success": True,
            "ideas": enriched_ideas,
            "trend_topic": trend_topic,
            "total_generated": len(enriched_ideas),
            "generation_time": generation_time
        }
        
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Failed to parse JSON response: {str(e)}",
            "ideas": [],
            "trend_topic": trend_topic,
            "total_generated": 0,
            "generation_time": round(time.time() - start_time, 2)
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Generation failed: {str(e)}",
            "ideas": [],
            "trend_topic": trend_topic,
            "total_generated": 0,
            "generation_time": round(time.time() - start_time, 2)
        }


def generate_detailed_script(
    idea: dict[str, Any],
    include_dialogue: bool = True
) -> dict[str, Any]:
    """Generate a detailed shot-by-shot script from a content idea.
    
    Args:
        idea: Content idea dict from generate_content_ideas()
        include_dialogue: Whether to include voiceover/dialogue text
        
    Returns:
        Dict containing:
        - success: bool
        - script: detailed script object
        - generation_time: seconds
    """
    
    start_time = time.time()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "success": False,
            "error": "OPENAI_API_KEY not found",
            "script": {},
            "generation_time": 0
        }
    
    try:
        # Build script generation prompt
        system_prompt = """You are an expert video script writer specialising in short-form content. You create detailed, shot-by-shot scripts that are easy to follow and optimised for high engagement."""
        
        dialogue_instruction = "Include specific voiceover/dialogue text for each shot." if include_dialogue else "Focus on visual directions without dialogue."
        
        user_prompt = f"""Create a detailed, actionable video script for this content idea:

IDEA OVERVIEW:
Title: {idea['title']}
Hook: {idea['hook']}
Angle: {idea['angle']}
Platform: {idea['platform']}
Duration: {idea['duration']}
Visual Style: {idea['visual_style']}

DESCRIPTION:
{idea['description']}

Create a shot-by-shot script with:
1. Shot number and timing (e.g., "Shot 1 (0:00-0:03)")
2. Visual description (what to film, camera angle, movement)
3. {'Voiceover/Dialogue text (exact words to say)' if include_dialogue else 'Visual focus (no dialogue)'}
4. Text overlays (if any)
5. Transitions (cuts, fades, effects)
6. Music/Sound cues (when to use trending sounds, music changes)

REQUIREMENTS:
- Total duration should match: {idea['duration']}
- Start with the hook: "{idea['hook']}"
- Include 5-8 shots minimum
- Be SPECIFIC about camera angles and movements
- {dialogue_instruction}
- Include timing for each shot
- Mention any props, locations, or setup needed
- Add notes for editing (pacing, effects, text timing)

Return as JSON:
{{
  "script_title": "{idea['title']}",
  "total_duration": "{idea['duration']}",
  "shots": [
    {{
      "shot_number": 1,
      "timing": "0:00-0:03",
      "visual": "Close-up of your face, hand covering mouth in shock",
      "dialogue": "Wait... they REALLY snubbed her?!" (only if include_dialogue is true, otherwise omit),
      "text_overlay": "The Grammy Snub ",
      "camera_notes": "Front camera, tight framing, eye-level",
      "transition": "Quick cut"
    }}
  ],
  "music_cues": ["Use trending shocked sound effect at 0:01", "Background music: upbeat trending sound"],
  "props_needed": ["Phone", "Ring light"],
  "location": "Well-lit room with plain background",
  "editing_notes": ["Fast cuts for first 10 seconds", "Add zoom effect on reactions", "Text overlays should be bold and centered"],
  "filming_tips": ["Film multiple takes of reactions", "Ensure good lighting", "Keep phone steady"]
}}"""

        print(f"\nGenerating detailed script for: {idea['title']}")
        
        # Call OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,  # Slightly lower for more structured output
            max_tokens=3500,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from OpenAI")
        
        script = json.loads(content)
        
        generation_time = round(time.time() - start_time, 2)
        
        print(f"   ✓ Script generated with {len(script.get('shots', []))} shots in {generation_time}s")
        
        return {
            "success": True,
            "script": script,
            "generation_time": generation_time
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Script generation failed: {str(e)}",
            "script": {},
            "generation_time": round(time.time() - start_time, 2)
        }

