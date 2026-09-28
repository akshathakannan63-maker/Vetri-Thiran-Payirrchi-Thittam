# ComicCraft

ComicCraft is an AI-powered web application that converts
a user's story idea into a five-panel comic.

The application uses:

- FastAPI
- HTML
- CSS
- JavaScript
- Jinja2
- Google Gemini
- Hugging Face image generation
- Stable Diffusion
- FPDF

---

# Project Structure

```text
ComicCraft/
│
├── app.py
├── config.py
├── ai.py
├── image_generator.py
├── pdf_generator.py
│
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
│
├── templates/
│   ├── index.html
│   └── result.html
│
├── static/
│   ├── style.css
│   └── script.js
│
└── generated/
    ├── images/
    └── pdfs/