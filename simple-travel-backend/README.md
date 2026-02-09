# Simple Travel Backend

Backend service for natural-language vacation rental search.

## Local Development

```bash
cp .env.example .env
conda run -n aieng pip install -r requirements.txt
conda run -n aieng gunicorn -w 2 -b 0.0.0.0:8001 app:app
```

## Required Environment Variables

- `GROQ_API_KEY`
- `GROQ_MODEL` (default in code: `llama-3.1-8b-instant`)
- `CORS_ORIGINS` (optional, comma-separated)

## Vercel

Deploy this folder as a separate Vercel project:

- Root Directory: `simple-travel-backend`
- Runtime: Python (via `api/index.py`)
- Config: `vercel.json`
- Environment Variables:
  - `GROQ_API_KEY`
  - `GROQ_MODEL`
  - `CORS_ORIGINS`
