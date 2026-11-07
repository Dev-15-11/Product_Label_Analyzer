# Product Label Analyzer

An API-first Python project that turns a product-label image into structured label data and an evidence-oriented research report. It combines image preprocessing, OCR, rule-based parsing, ingredient normalization, schema-validated AI research, and PDF generation.

## Project highlights

- Accepts JPEG and PNG label images through a FastAPI endpoint.
- Corrects image orientation, extracts text with Tesseract OCR, and reports OCR confidence.
- Parses ingredients, product claims, warnings, and usage instructions into Pydantic models.
- Normalizes common ingredient aliases (for example, `Aqua` to `water`).
- Uses OpenRouter with web search for research, validates the response against a typed schema, and generates a downloadable PDF with findings, sources, and limitations.
- Includes unit tests for parsing, models, configuration, client response validation, and OCR edge cases.

## Review the work

| What to review | Example |
|---|---|
| Generated research report | [Dove](examples/reports/Dove_research_report.pdf) · [Godrej](examples/reports/Godrej_research_report.pdf) · [Parle G](examples/reports/G%20Parle_research_report.pdf) |
| System design | [Revised architecture](docs/architecture/product_label_analyzer_architecture_revised.pdf) |
| Sample label inputs | [Dettol](examples/labels/Dettol.jpg) · [Dove](examples/labels/Dove.png) · [Godrej](examples/labels/Godrej.jpg) · [Parle G](examples/labels/Parle%20G.jpg) |

These reports are generated examples, not authoritative product-safety or compliance assessments. Review their cited sources and limitations. Before publishing, confirm you have the right to redistribute the sample product-label images and generated reports.

## How it works

1. The upload endpoint validates the file type, size, and image dimensions.
2. The image is orientation-corrected and preprocessed for OCR.
3. Tesseract extracts text and confidence values; the parser structures the recognized label sections.
4. Ingredient aliases are normalized.
5. The research flow submits structured label data to OpenRouter's web-search-enabled model, validates the returned report, and streams a PDF to the caller.

## Run locally

### Requirements

- Python 3.10 or newer
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed and available on `PATH`
- An [OpenRouter API key](https://openrouter.ai/keys) for research and AI assessment endpoints

If Tesseract is not on `PATH`, set `TESSERACT_CMD` in `.env` to the executable's full path.

### Install

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Add your key to `.env`:

```dotenv
OPENROUTER_API_KEY=your_key_here
```

The model settings in `.env.example` can be changed if needed. Keep `.env` private; it is excluded from Git.

### Start the API

```powershell
python -m uvicorn app.main:app --reload
```

To upload a sample image and save the generated PDF:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/upload-label" `
  -F "file=@examples/labels/Dettol.jpg" `
  --output Dettol_research_report.pdf
```

The upload endpoint accepts JPEG/PNG files up to 10 MB. It stores the source and processed images under `data/uploads/` and `data/processed/`; those runtime files are ignored by Git.

### Run tests

```powershell
python -m pytest -q
```

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Basic API status |
| `GET` | `/health` | Health check |
| `POST` | `/upload-label` | Upload a label, run OCR and web research, and download a PDF report |
| `POST` | `/analyze-label/{saved_filename}` | Return extracted text, parsed fields, OCR confidence, and normalized ingredients for a saved image |
| `POST` | `/assess-label/{saved_filename}` | Return a structured claim/ingredient assessment for a saved image |

The assessment endpoint currently supplies no external evidence to the assessment model, so results can be `UNABLE_TO_VERIFY`. The research PDF flow is separate and uses the OpenRouter web-search plugin.

## Project layout

```text
app/
  models/       Pydantic request/response and report models
  services/     OCR, parsing, normalization, research, and PDF generation
  main.py       FastAPI routes
  config.py     Environment-based configuration
tests/          Focused unit tests
examples/
  labels/       Sample input images
  reports/      Example generated research PDFs
docs/
  architecture/ Architecture documents
data/           Local uploads and processed images (Git-ignored)
```

## Limitations and responsible use

- OCR can misread small, curved, blurry, or low-contrast labels; review the extracted text and confidence before relying on results.
- AI-generated research can be incomplete or incorrect. Check the cited sources directly; missing or ambiguous evidence should not be treated as confirmation.
- Reports are informational only, not medical, legal, or regulatory advice.
- This project is an unauthenticated local-development API. Do not expose it publicly without adding authentication, rate limiting, upload-retention controls, and an appropriate privacy notice. Uploaded label data is sent to OpenRouter for research.

## License

No license is currently included. Please confirm the license you want before publishing so others know how they may use the code.
