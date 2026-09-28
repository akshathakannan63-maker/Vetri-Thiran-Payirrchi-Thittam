from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from huggingface_hub import InferenceClient

from config import (
    DEMO_MODE,
    GENERATED_IMAGES_DIR,
    HF_API_KEY,
    IMAGE_MODEL,
)


# ============================================================
# DEMO IMAGE
# ============================================================

def create_demo_image(
    prompt: str,
    panel_number: int,
) -> Path:
    """
    Create a simple placeholder image.

    This allows the project to run without
    a Hugging Face API key.
    """

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    filename = (
        f"panel_{panel_number}_"
        f"{timestamp}.png"
    )

    output_path = (
        GENERATED_IMAGES_DIR
        / filename
    )

    width = 1024
    height = 768

    image = Image.new(
        "RGB",
        (width, height),
        "white",
    )

    draw = ImageDraw.Draw(
        image
    )

    try:

        title_font = ImageFont.truetype(
            "arial.ttf",
            42,
        )

        body_font = ImageFont.truetype(
            "arial.ttf",
            24,
        )

    except OSError:

        title_font = ImageFont.load_default()

        body_font = ImageFont.load_default()

    # Border

    draw.rectangle(
        (
            20,
            20,
            width - 20,
            height - 20,
        ),
        outline="black",
        width=8,
    )

    # Title

    draw.text(
        (55, 50),
        f"ComicCraft - Panel {panel_number}",
        fill="black",
        font=title_font,
    )

    # Demo notice

    draw.text(
        (55, 125),
        "DEMO MODE",
        fill="black",
        font=body_font,
    )

    draw.text(
        (55, 165),
        "Enable DEMO_MODE=false",
        fill="black",
        font=body_font,
    )

    draw.text(
        (55, 200),
        "to generate real AI artwork.",
        fill="black",
        font=body_font,
    )

    # Prompt wrapping

    words = prompt.split()

    lines = []

    current_line = ""

    for word in words:

        candidate = (
            current_line
            + " "
            + word
        ).strip()

        if len(candidate) > 60:

            lines.append(
                current_line
            )

            current_line = word

        else:

            current_line = candidate

    if current_line:
        lines.append(
            current_line
        )

    y = 280

    for line in lines[:12]:

        draw.text(
            (55, y),
            line,
            fill="black",
            font=body_font,
        )

        y += 35

    # Simple character placeholder

    draw.ellipse(
        (
            730,
            430,
            900,
            600,
        ),
        outline="black",
        width=5,
    )

    draw.rectangle(
        (
            760,
            580,
            870,
            700,
        ),
        outline="black",
        width=5,
    )

    image.save(
        output_path,
        format="PNG",
    )

    return output_path


# ============================================================
# REAL IMAGE GENERATION
# ============================================================

def generate_real_image(
    prompt: str,
) -> Image.Image:
    """
    Generate an image using Hugging Face.
    """

    if not HF_API_KEY:

        raise RuntimeError(
            "HF_API_KEY is missing. "
            "Add it to .env."
        )

    client = InferenceClient(
        api_key=HF_API_KEY,
        provider="auto",
    )

    image = client.text_to_image(
        prompt=prompt,

        model=IMAGE_MODEL,

        negative_prompt=(
            "blurry, low quality, distorted face, "
            "bad anatomy, duplicate character, "
            "extra limbs, extra fingers, "
            "watermark, unreadable text"
        ),
    )

    return image


# ============================================================
# MAIN IMAGE GENERATOR
# ============================================================

def generate_comic_image(
    prompt: str,
    panel_number: int,
) -> str:
    """
    Generate one comic panel image.

    Returns the full local image path.
    """

    if DEMO_MODE:

        image_path = create_demo_image(
            prompt=prompt,
            panel_number=panel_number,
        )

        return str(image_path)

    image = generate_real_image(
        prompt
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    filename = (
        f"panel_{panel_number}_"
        f"{timestamp}.png"
    )

    output_path = (
        GENERATED_IMAGES_DIR
        / filename
    )

    image.save(
        output_path
    )

    return str(
        output_path
    )