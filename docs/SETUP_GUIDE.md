# Setup Guide

Operational notes for running and debugging the current stack.

## Required credentials

### OpenAI

1. https://platform.openai.com/api-keys → create a secret key
2. Put it in `backend/.env` as `OPENAI_API_KEY`

Model used: `gpt-4o-mini` in `backend/chat_engine.py` (change there if you want another model).

### Supabase

1. Project URL + **anon** key in `.env`
2. Run SQL in order (see [SUPABASE_SETUP.md](SUPABASE_SETUP.md)):
   - `backend/sql/supabase_setup.sql`
   - `backend/sql/saved_products_setup.sql`
   - `backend/sql/chat_history_setup.sql`
3. Email auth on; **Confirm email off** for local demos

---

## How the pieces fit

| Piece | What it stores / does |
|-------|------------------------|
| Supabase `products` | Shared catalog + review JSON (source of truth) |
| Supabase `saved_products` | Per-user interest + note |
| Supabase `chat_messages` | Per-user chat history + citation payloads |
| Chroma | Embedding index for top-k review retrieval (RAG) |
| localStorage | Auth session JWT only |

Chat answers use retrieved reviews only; conflicting reviews should be summarized with citations (see system prompt in `chat_engine.py`).

---

## Auth UX notes

- Users sign up with **username**, not email
- Backend maps username → `username@users.local` for Supabase Auth
- Valid username: `[a-zA-Z0-9_]{3,30}`
- After API/auth changes, restart the backend
- Stuck “email not confirmed” users: delete in Supabase Auth → Users, sign up again

---

## Chroma / RAG demo notes

- Chroma backs similarity search so the demo shows a real RAG path
- Process-local index: **restarting the API clears embeddings** even if Supabase still has products
- Fix for local use: with the server running, `python upload_sample_data.py` (or re-upload a product via the UI)
- Production-minded next steps (not implemented): durable Chroma persist, rebuild-from-Supabase on startup, or pgvector in Supabase

---

## Common failures

| Symptom | Check |
|---------|--------|
| FastAPI / module import errors | `source venv/bin/activate`; broken venv → recreate |
| Chat empty / “no reviews indexed” | Embeddings missing after restart → re-run upload script |
| Vague “mixed / unclear” answers | Prompt/rules in `chat_engine.py` (should cite both sides) |
| Saved / history HTTP 400 | Missing SQL tables or RLS |
| Signup / sign-in fails | Confirm email disabled? Username format? Backend restarted? |
| OpenAI 429 | Billing / rate limits on the OpenAI account |
| CORS | Frontend origin must be allowed; default local ports 3000 → 8000 |

---

## Optional later improvements

- Persist or auto-rebuild the vector index
- Stricter RLS on `products` for production
- Deploy API (Railway, Fly, etc.) + static frontend (Vercel/Netlify)
- Rate limiting / HTTPS at the reverse proxy

These are optional; the app already uses Supabase for persistence and Auth for multi-user saved products and history.
