# Hotel Finder Monorepo

This repository contains:

- `simple-travel-website`: Next.js frontend
- `simple-travel-backend`: Flask backend

## Local Run

1. Start backend:

```bash
cd simple-travel-backend
conda run -n aieng gunicorn -w 2 -b 0.0.0.0:8001 app:app
```

2. Start frontend in another terminal:

```bash
cd simple-travel-website
cp .env.example .env.local
npm run dev -- -H 127.0.0.1 -p 3001
```

3. Open:

- `http://127.0.0.1:3001/hotels`

## Vercel Deployment (Monorepo)

Create two Vercel projects from this same repo:

1. Backend project
   - Root Directory: `simple-travel-backend`
   - Env Vars: `GROQ_API_KEY`, `GROQ_MODEL`, `CORS_ORIGINS`

2. Frontend project
   - Root Directory: `simple-travel-website`
   - Env Var: `NEXT_PUBLIC_API_BASE_URL=<backend-vercel-url>`
