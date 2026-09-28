from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ai import generate_comic_content
from config import (
    APP_NAME,
    GENERATED_IMAGES_DIR,
    GENERATED_PDFS_DIR,
    TEMPLATES_DIR,
    STATIC_DIR,
)
from image_generator import generate_comic_image
from pdf_generator import create_comic_pdf


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title=APP_NAME,
    description="AI Comic Story Creator using Gemini and Stable Diffusion",
    version="1.0.0",
)


# ============================================================
# DIRECTORIES
# ============================================================

GENERATED_IMAGES_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

GENERATED_PDFS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# STATIC FILES
# ============================================================

app.mount(
    "/static",
    StaticFiles(
        directory=str(STATIC_DIR)
    ),
    name="static",
)

app.mount(
    "/generated",
    StaticFiles(
        directory=str(Path("generated"))
    ),
    name="generated",
)


# ============================================================
# TEMPLATES
# ============================================================

templates = Jinja2Templates(
    directory=str(TEMPLATES_DIR)
)


# ============================================================
# HOME PAGE
# ============================================================

@app.get("/")
async def home(request: Request):
    """
    Display the ComicCraft input page.
    """

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "title": "ComicCraft",
        },
    )


# ============================================================
# GENERATE COMIC
# ============================================================

@app.post(
    "/generate",
    response_class=HTMLResponse,
)
async def generate_comic(
    request: Request,

    story_prompt: str = Form(...),

    character_name: str = Form(...),

    setting: str = Form(...),

    tone: str = Form(...),

    art_style: str = Form(...),
):
    """
    Generate the complete comic.

    Workflow:

    1. Receive user input
    2. Generate comic outline
    3. Generate narration and dialogue
    4. Generate images
    5. Create PDF
    6. Display result page
    """

    form_data = {
        "story_prompt": story_prompt,
        "character_name": character_name,
        "setting": setting,
        "tone": tone,
        "art_style": art_style,
    }

    try:

        # ----------------------------------------------------
        # STEP 1
        # Generate story content using Gemini
        # ----------------------------------------------------

        comic_data = generate_comic_content(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        panels = comic_data["panels"]

        # ----------------------------------------------------
        # STEP 2
        # Generate image for every panel
        # ----------------------------------------------------

        for panel in panels:

            image_path = generate_comic_image(
                prompt=panel["image_prompt"],
                panel_number=panel["panel_number"],
            )

            panel["image_path"] = image_path

            panel["image_url"] = (
                "/generated/images/"
                + Path(image_path).name
            )

        # ----------------------------------------------------
        # STEP 3
        # Generate PDF
        # ----------------------------------------------------

        pdf_path = create_comic_pdf(
            title=comic_data["title"],
            panels=panels,
        )

        pdf_url = (
            "/generated/pdfs/"
            + Path(pdf_path).name
        )

        # ----------------------------------------------------
        # STEP 4
        # Display result
        # ----------------------------------------------------

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "request": request,
                "title": comic_data["title"],
                "panels": panels,
                "pdf_url": pdf_url,
            },
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "request": request,
                "title": "ComicCraft",
                "error": str(exc),
                "form": form_data,
            },
            status_code=500,
        )


# ============================================================
# JSON API
# ============================================================

@app.post(
    "/api/generate",
)
async def generate_comic_api(
    data: dict,
):
    """
    JSON API endpoint.

    Example request:

    {
        "story_prompt": "...",
        "character_name": "Ravi",
        "setting": "Forest",
        "tone": "Dramatic",
        "art_style": "Comic Book"
    }
    """

    required_fields = [
        "story_prompt",
        "character_name",
        "setting",
        "tone",
        "art_style",
    ]

    for field in required_fields:

        if not data.get(field):

            return JSONResponse(
                status_code=400,
                content={
                    "error": (
                        f"Missing required field: "
                        f"{field}"
                    )
                },
            )

    try:

        comic_data = generate_comic_content(
            story_prompt=data["story_prompt"],
            character_name=data["character_name"],
            setting=data["setting"],
            tone=data["tone"],
            art_style=data["art_style"],
        )

        for panel in comic_data["panels"]:

            image_path = generate_comic_image(
                prompt=panel["image_prompt"],
                panel_number=panel["panel_number"],
            )

            panel["image_path"] = image_path

            panel["image_url"] = (
                "/generated/images/"
                + Path(image_path).name
            )

        pdf_path = create_comic_pdf(
            title=comic_data["title"],
            panels=comic_data["panels"],
        )

        comic_data["pdf_url"] = (
            "/generated/pdfs/"
            + Path(pdf_path).name
        )

        return comic_data

    except Exception as exc:

        return JSONResponse(
            status_code=500,
            content={
                "error": str(exc)
            },
        )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health():
    """
    Check whether the application is running.
    """

    from config import (
        DEMO_MODE,
        GEMINI_API_KEY,
        HF_API_KEY,
    )

    return {
        "status": "ok",
        "application": APP_NAME,
        "demo_mode": DEMO_MODE,
        "gemini_configured": bool(
            GEMINI_API_KEY
        ),
        "huggingface_configured": bool(
            HF_API_KEY
        ),
    }


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )