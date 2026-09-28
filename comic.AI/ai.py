import json
from functools import lru_cache

from google import genai
from google.genai import types

from config import (
    DEMO_MODE,
    GEMINI_API_KEY,
    GEMINI_FLASH_MODEL,
    GEMINI_PRO_MODEL,
    NUMBER_OF_PANELS,
)


# ============================================================
# GEMINI CLIENT
# ============================================================

@lru_cache(maxsize=1)
def get_gemini_client():
    """
    Create one reusable Gemini client.
    """

    if not GEMINI_API_KEY:

        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add it to your .env file."
        )

    return genai.Client(
        api_key=GEMINI_API_KEY
    )


# ============================================================
# DEMO DATA
# ============================================================

def create_demo_comic(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
):
    """
    Generate sample comic content without
    calling an external AI service.

    This is useful for testing the application.
    """

    panels = [

        {
            "panel_number": 1,
            "title": "A New Beginning",
            "scene_description": (
                f"{character_name} begins an "
                f"unexpected adventure in the "
                f"{setting}."
            ),
            "caption": (
                "Every adventure begins with "
                "one small step."
            ),
            "narration": (
                f"{character_name} looks around "
                f"the {setting}, unaware that "
                "something extraordinary is about "
                "to happen."
            ),
            "dialogue": (
                "I wonder what is waiting for me."
            ),
            "image_prompt": (
                f"{character_name} standing in a "
                f"beautiful {setting}, beginning "
                f"an adventure, {art_style} comic "
                f"book illustration, {tone} mood, "
                "cinematic composition."
            ),
        },

        {
            "panel_number": 2,
            "title": "The Mystery",
            "scene_description": (
                f"A strange discovery catches "
                f"{character_name}'s attention."
            ),
            "caption": (
                "Something unusual appears."
            ),
            "narration": (
                f"{character_name} discovers a "
                "mysterious clue hidden nearby."
            ),
            "dialogue": (
                "What could this mean?"
            ),
            "image_prompt": (
                f"{character_name} discovering a "
                f"mysterious object in the {setting}, "
                f"{art_style} comic illustration, "
                f"{tone} atmosphere."
            ),
        },

        {
            "panel_number": 3,
            "title": "The Challenge",
            "scene_description": (
                f"The discovery leads "
                f"{character_name} toward a "
                "dangerous challenge."
            ),
            "caption": (
                "The path ahead is not easy."
            ),
            "narration": (
                f"{character_name} realizes that "
                "the mystery cannot be solved "
                "without taking a risk."
            ),
            "dialogue": (
                "I have to keep going."
            ),
            "image_prompt": (
                f"{character_name} facing a dramatic "
                f"challenge in the {setting}, "
                f"dynamic action, {art_style} comic "
                f"book style, {tone} lighting."
            ),
        },

        {
            "panel_number": 4,
            "title": "The Turning Point",
            "scene_description": (
                f"{character_name} finds the "
                "courage to overcome the challenge."
            ),
            "caption": (
                "Courage changes everything."
            ),
            "narration": (
                f"With determination, "
                f"{character_name} finds a way "
                "forward and finally understands "
                "the meaning of the mystery."
            ),
            "dialogue": (
                "I can do this!"
            ),
            "image_prompt": (
                f"{character_name} overcoming a "
                f"major challenge in the {setting}, "
                f"heroic pose, {art_style} comic "
                f"illustration, dramatic {tone} mood."
            ),
        },

        {
            "panel_number": 5,
            "title": "A New Chapter",
            "scene_description": (
                f"The adventure ends with "
                f"{character_name} looking toward "
                "a new future."
            ),
            "caption": (
                "And so a new chapter begins."
            ),
            "narration": (
                f"{character_name} returns from "
                "the adventure with new confidence "
                "and a story worth remembering."
            ),
            "dialogue": (
                "This is only the beginning."
            ),
            "image_prompt": (
                f"{character_name} standing proudly "
                f"in the {setting} at sunset, "
                f"looking toward the future, "
                f"{art_style} comic book illustration, "
                f"hopeful {tone} atmosphere."
            ),
        },
    ]

    return {
        "title": (
            f"{character_name}'s "
            "Comic Adventure"
        ),
        "panels": panels,
    }


# ============================================================
# GENERATE OUTLINE WITH GEMINI FLASH
# ============================================================

def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
):
    """
    Gemini Flash creates the structured
    five-panel comic outline.
    """

    client = get_gemini_client()

    prompt = f"""
You are the outline writer for ComicCraft.

Create exactly {NUMBER_OF_PANELS} panels.

User story idea:
{story_prompt}

Main character:
{character_name}

Setting:
{setting}

Tone:
{tone}

Art style:
{art_style}

The story must have:

1. A clear beginning.
2. A developing situation.
3. A conflict or challenge.
4. A climax or turning point.
5. A satisfying ending.

Return ONLY valid JSON.

Use this exact structure:

{{
  "title": "Comic title",
  "panels": [
    {{
      "panel_number": 1,
      "title": "Panel title",
      "scene_description": "Scene description",
      "image_prompt": "Detailed image prompt"
    }}
  ]
}}

There must be exactly {NUMBER_OF_PANELS} panels.

Keep the same character visually consistent
throughout every panel.
"""


    response = client.models.generate_content(
        model=GEMINI_FLASH_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.8,
        ),
    )

    text = response.text

    if not text:
        raise RuntimeError(
            "Gemini Flash returned an empty response."
        )

    return json.loads(text)


# ============================================================
# GENERATE STORY WITH GEMINI PRO
# ============================================================

def generate_story(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
    outline: dict,
):
    """
    Gemini Pro expands the outline into
    narration, captions and dialogue.
    """

    client = get_gemini_client()

    outline_json = json.dumps(
        outline,
        indent=2,
        ensure_ascii=False,
    )

    prompt = f"""
You are the creative story writer for ComicCraft.

Create the narration and dialogue for a
five-panel comic.

Original story idea:
{story_prompt}

Main character:
{character_name}

Setting:
{setting}

Tone:
{tone}

Art style:
{art_style}

The generated outline is:

{outline_json}

Return ONLY valid JSON.

Use this structure:

{{
  "title": "Comic title",
  "panels": [
    {{
      "panel_number": 1,
      "caption": "Short comic caption",
      "narration": "Narration for the panel",
      "dialogue": "Character dialogue"
    }}
  ]
}}

Requirements:

- Exactly {NUMBER_OF_PANELS} panels.
- Keep the same protagonist.
- Maintain continuity.
- Make the dialogue concise.
- Make narration vivid.
- Match the requested tone.
- Do not include markdown.
"""


    response = client.models.generate_content(
        model=GEMINI_PRO_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.9,
        ),
    )

    text = response.text

    if not text:
        raise RuntimeError(
            "Gemini Pro returned an empty response."
        )

    return json.loads(text)


# ============================================================
# MERGE AI RESULTS
# ============================================================

def merge_comic_data(
    outline: dict,
    story: dict,
):
    """
    Combine outline and story information
    into one final panel structure.
    """

    story_panels = {
        panel["panel_number"]: panel
        for panel in story["panels"]
    }

    final_panels = []

    for panel in outline["panels"]:

        number = panel["panel_number"]

        story_panel = story_panels.get(
            number
        )

        if story_panel is None:

            raise RuntimeError(
                f"Missing story panel {number}."
            )

        final_panels.append(
            {
                "panel_number": number,

                "title": panel["title"],

                "scene_description": (
                    panel["scene_description"]
                ),

                "image_prompt": (
                    panel["image_prompt"]
                ),

                "caption": (
                    story_panel.get(
                        "caption",
                        "",
                    )
                ),

                "narration": (
                    story_panel.get(
                        "narration",
                        "",
                    )
                ),

                "dialogue": (
                    story_panel.get(
                        "dialogue",
                        "",
                    )
                ),
            }
        )

    return {
        "title": story.get(
            "title",
            outline.get(
                "title",
                "ComicCraft Comic",
            ),
        ),
        "panels": final_panels,
    }


# ============================================================
# MAIN AI PIPELINE
# ============================================================

def generate_comic_content(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
):
    """
    Main AI pipeline.

    Flash:
        Generates structured outline.

    Pro:
        Generates narration/dialogue.

    Then both results are merged.
    """

    if DEMO_MODE:

        return create_demo_comic(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

    outline = generate_outline(
        story_prompt=story_prompt,
        character_name=character_name,
        setting=setting,
        tone=tone,
        art_style=art_style,
    )

    story = generate_story(
        story_prompt=story_prompt,
        character_name=character_name,
        setting=setting,
        tone=tone,
        art_style=art_style,
        outline=outline,
    )

    return merge_comic_data(
        outline,
        story,
    )