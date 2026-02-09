# Current Implementation Flow (Backend)

## Scope
This document describes the backend as implemented now in `simple-travel-backend`, including active runtime flow and non-active/redundant code paths.

## Intended Product Role
The backend is a natural-language filter service over a local Airbnb-style listings CSV:
1. Accept user query text.
2. Use an LLM to generate a pandas filter expression.
3. Execute that expression against a local DataFrame.
4. Return filtered listing cards plus inferred filter labels.

## Runtime Entry Points
- Main web app: `app.py`
- Main endpoint used by frontend: `POST /chat` (`app.py:82`)
- Secondary/testing endpoint: `/test` (`app.py:119`)

## End-to-End Runtime Flow

### 1) Process startup (`app.py`)
1. Flask app and CORS are initialized (`app.py:13-14`).
2. Environment variables are loaded via `.env` (`app.py:16`).
3. LangChain prompt template is derived from `chat_config.HOTEL_QUERY_PROMPT` by converting `$context/$query` placeholders to `{context}/{query}` (`app.py:20-22`).
4. The LangChain chain is lazily initialized on first non-`firstcall` query by `get_query_chain()` (`app.py:26`), using:
   - `ChatGroq` model provider (`app.py:31-36`)
   - Model from `GROQ_MODEL` (default `llama-3.1-8b-instant`) (`app.py:19`, `app.py:33`)
   - `StrOutputParser` for text output (`app.py:39`)

### 2) Data source loading
- Listings are loaded from one hardcoded file in `load_original()`:
  - `./clean/dataset_airbnb-scraper_2024-04-26_08-50-51-029.csv` (`app.py:18`, `app.py:44`)
- A fixed set of numeric columns is coerced on each load (`app.py:47-62`).

### 3) `POST /chat` request flow (`app.py:82`)
1. Reads JSON body and validates required `query` field (`app.py:95-102`).
2. If query equals `"firstcall"`:
   - Loads full CSV.
   - Returns unfiltered listings and empty filter badges (`app.py:85-88`).
3. Otherwise:
   - Runs the LangChain query-generation chain with `{context: "", query: <user query>}` (`app.py:73-75`).
   - Normalizes fenced code output if present (`app.py:66-71`).
   - Executes generated pandas expression via `exec("mydf=" + dataframe_query, ...)` (`app.py:95-96`).
   - Extracts referenced DataFrame columns via regex and maps with `EASY_NAME_MAP` (`app.py:77-80`, `chat_config.py:291`).
   - Catches LLM and query-execution failures and returns structured JSON errors (no HTML traceback responses) (`app.py:109-136`).
4. Returns a fixed frontend payload projection/rename (`app.py:101-108`).
5. Response JSON shape:
   - `filters`: user-friendly filter names.
   - `listings`: listing cards (`app.py:111-112`).
   - Optional `error`: `{type, message}` on failure (`app.py:76-80`).

### 4) `/test` endpoint status (`app.py:119`)
- Still demo/stub oriented.
- POST path is hardcoded to `rtype = "table"` (`app.py:126`).
- It reads `./clean/bangkok-supabase-sample.csv` if present, else falls back to `load_original()` (`app.py:138-143`).
- Not needed by the main `/chat` flow.

## Prompt and Schema Configuration (`chat_config.py`)
- Active for runtime filtering:
  - `HOTEL_QUERY_PROMPT` (`chat_config.py:44`) controls NL -> pandas conversion behavior.
  - `EASY_NAME_MAP` (`chat_config.py:291`) controls frontend badge labels.
- Legacy/non-core:
  - `DEFAULT_PROMPT_WITH_HISTORY` and `DEFAULT_PROMPT_WITHOUT_HISTORY` are finance-domain leftovers (`chat_config.py:3`, `chat_config.py:27`).
- `FINAL_COLUMNS` is used by offline preprocessing, not directly by `/chat` runtime (`chat_config.py:141`).

## Data Preparation Flow (Offline Script)
- Script: `hotel-data-transformer.py`
- Purpose: process raw scraper CSV files from `references/` into cleaned artifacts in `clean/`.
- Pipeline:
1. Drop broad groups of noisy columns (`hotel-data-transformer.py:7`).
2. Flatten and rename amenity columns (`hotel-data-transformer.py:19`).
3. Flatten review summary columns (`hotel-data-transformer.py:43`).
4. Limit number of photo columns (`hotel-data-transformer.py:55`).
5. Drop mostly-null columns (`hotel-data-transformer.py:72`).
6. Convert amenity/allow booleans to ints (`hotel-data-transformer.py:100`).
7. Derive `bed_count`, `bathroom_count`, `bedroom_count` (`hotel-data-transformer.py:113-115`).
8. Keep intersection with `chat_config.FINAL_COLUMNS` and persist (`hotel-data-transformer.py:116-118`, `hotel-data-transformer.py:148`).

## External Dependencies Matrix

### Required for primary `/chat` behavior
- Groq API + key (`GROQ_API_KEY`)
  - Used in LangChain `ChatGroq` initialization (`app.py:28-36`).
  - Required for non-`firstcall` NL query conversion.
- Local cleaned CSV dataset
  - `clean/dataset_airbnb-scraper_2024-04-26_08-50-51-029.csv` (`app.py:18`, `app.py:44`).
  - Required for listing output.

### Present in repo but not required by current `/chat` runtime
- Chroma config/compose assets (e.g. `db/chroma-compose.yml`): not wired into active request path.
- OpenAI/Supabase/Postgres references in notebooks or notes: not used in active Flask endpoint flow.

## Cleanup Notes Applied
- Runtime now uses LangChain (`ChatGroq`) instead of Embedchain.
- Unused imports removed from `app.py`.
- `/test` endpoint no longer hard-fails when sample file is missing.
- Secret-like token in `instructions.txt` has been redacted.
- README env setup now reflects the active runtime dependency (`GROQ_API_KEY`).

## Important Behavioral Risks (Still Present by Design)
- Dynamic code execution remains core behavior:
  - LLM output is executed with `exec` (`app.py:96`).
- Badge mapping is best-effort:
  - Unknown columns fall back to raw names (`app.py:79`).
- Naming mismatch still exists in config:
  - Prompt/schema uses `amenity_Hot_water` (`chat_config.py:95`, `chat_config.py:195`).
  - `EASY_NAME_MAP` uses `amenity_Hot water` (`chat_config.py:329`).

## What Powers the Demo Today
If frontend uses `/chat`, the live behavior depends mainly on:
1. Flask endpoint logic in `app.py`.
2. LangChain + Groq for NL-to-pandas conversion.
3. Local cleaned CSV data in `clean/`.

No active database service is required for the core listing-filter demo path.
