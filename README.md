# GenAI Medical Policy Analyzer

AI-powered tool that extracts and compares critical data fields from medical insurance policy PDFs across multiple insurers using OpenAI GPT-4o-mini.

---

## UI/UX Transition: Streamlit → Google Stitch

The UI was redesigned using **Google Stitch** — replacing the original Streamlit interface with a professional healthcare SaaS dashboard built in HTML/Tailwind CSS, served by a Flask backend.

### Before — Streamlit UI
![Streamlit UI](ui/screenshots/streamlit_before.png)

### After — Google Stitch UI
![Stitch Dashboard](ui/screenshots/stitch_live_dashboard.png)

![Stitch Results](ui/screenshots/stitch_live_results.png)

**What changed:**
- Static Streamlit components → Stitch-generated Tailwind CSS + Material Symbols design system
- Streamlit server → Flask REST API (`/api/analyze`, `/api/demo`)
- Custom healthcare color scheme (`#1A237E` navy, `#1565c0` blue)
- Interactive policy comparison table rendered from markdown
- Real-time demo mode toggle with instant results
- Drag-and-drop PDF upload with file count indicator

---

## Features

- Upload multiple medical policy PDFs (local drag-and-drop or AWS S3)
- Automatically extract 18 standardized fields per policy
- Side-by-side comparison table across insurers (Aetna, UnitedHealth, Cigna, etc.)
- Demo Mode — no credentials required to explore the UI
- OpenAI GPT-4o-mini for intelligent policy text analysis
- Flask REST API with endpoints: `GET /`, `POST /api/analyze`, `POST /api/demo`

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI / Design | Google Stitch + HTML/Tailwind CSS |
| UI Framework (legacy) | Streamlit (`main_streamlit.py`) |
| Backend | Python / Flask |
| AI Engine | OpenAI GPT-4o-mini |
| PDF Parsing | PyPDF2 |
| Cloud Storage | AWS S3 / boto3 |
| Config | python-dotenv |

---

## Project Structure

```
├── server.py              # Flask server (primary entry point)
├── main_streamlit.py      # Legacy Streamlit UI (archived)
├── langchain_helper1.py   # PDF extraction + OpenAI analysis backend
├── app.py                 # Alternative S3-only analyzer
├── readfile.py / readfile2.py  # PDF reader utilities
├── requirements.txt
├── .env.example
├── ui/
│   ├── index.html         # Stitch-generated dashboard (primary UI)
│   ├── results.html       # Stitch-generated results screen
│   └── screenshots/
│       ├── streamlit_before.png      # Before: Streamlit UI
│       ├── stitch_live_dashboard.png # After: Stitch dashboard
│       └── stitch_live_results.png   # After: Stitch results
```

---

## Setup

```bash
git clone https://github.com/atharvadevne123/GenAI-Medical-Policy-Analysis
cd GenAI-Medical-Policy-Analysis
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill in OPENAI_API_KEY and AWS credentials in .env
```

### Run the app

```bash
python server.py
# Open http://localhost:5000
```

Use **Demo Mode** in the sidebar to explore without credentials.

---

## Extracted Fields

Policy Number · Title · Policy Criteria · Age Criteria · Insurance Company · Insurance Type ·
Service Type · Status · Effective Date · Last Review · Next Review · Guideline Source ·
States Covered · Prior Authorization · Exclusions/Limitations · Coverage Period · Related Policies · Link to Policy

---

## Author

**Atharva Devne**
