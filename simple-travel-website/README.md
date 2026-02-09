# Simple Travel Website

Frontend for natural-language vacation rental search in Bangkok.

## Local Development

```bash
cp .env.example .env.local
npm install
npm run dev -- -H 127.0.0.1 -p 3001
```

Set `NEXT_PUBLIC_API_BASE_URL` in `.env.local`:

```bash
NEXT_PUBLIC_API_BASE_URL="http://localhost:8001"
```

Then open `http://127.0.0.1:3001/hotels`.

## Vercel

Deploy this folder as a separate Vercel project with:

- Framework Preset: `Next.js`
- Root Directory: `simple-travel-website`
- Environment Variable: `NEXT_PUBLIC_API_BASE_URL=<your-backend-vercel-url>`
