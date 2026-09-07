# Upload Sample Data

Upload MacBook Pro and iPhone sample products into Supabase and build Chroma embeddings for RAG.

## Prerequisites

1. Supabase project ready
2. `backend/sql/supabase_setup.sql` run (products table)
3. `backend/.env` with Supabase + OpenAI keys
4. Backend dependencies installed (`pip install -r requirements.txt`)
5. Images under `frontend/images/` (if you care about thumbnails)
6. **Backend server running** on `http://localhost:8000` (upload script calls the API)

Saved products / chat history SQL are not required for upload, but you need them for those UI features.

---

## Method 1: Upload script (recommended)

### Terminal 1 — API

```bash
cd backend
source venv/bin/activate
python main.py
```

### Terminal 2 — upload

```bash
cd backend
source venv/bin/activate
python upload_sample_data.py
```

Expected: both products succeed, 20 reviews each. The script deletes and re-uploads if a product already exists.

**Important:** After every backend restart, run the upload script again (with the server up) so Chroma has embeddings. Supabase still has the rows; the vector index does not survive restart in the current demo setup.

---

## Method 2: Web UI

1. Start backend + frontend (`python3 -m http.server 3000` in `frontend/`)
2. Sign in at http://localhost:3000
3. Use **+ Upload Product** and paste fields from `sample_products.json`

---

## Method 3: API (cURL)

```bash
curl -X POST http://localhost:8000/api/products/upload \
  -H "Content-Type: application/json" \
  -d @- <<'EOF'
{ ... product JSON ... }
EOF
```

Prefer the script or UI unless you need raw API testing. Full payloads live in `sample_products.json` at the repo root.

---

## Verify

**Supabase** → Table Editor → `products` → `macbook_pro_m3_2024`, `iphone_15_pro_max_2024`

**API**

```bash
curl http://localhost:8000/api/products
```

**UI** — product list on the left; ask a question and check that sources/citations appear.

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| Cannot connect to API | Start `python main.py` first |
| Product already exists | Script usually deletes/retries; or `DELETE /api/products/{id}` then re-run |
| `SUPABASE_URL` / key issues | Check `backend/.env` |
| `relation "products" does not exist` | Run `backend/sql/supabase_setup.sql` |
| Chat finds 0 documents | Re-run `upload_sample_data.py` after backend restart |
| Images missing | Paths like `images/mbp.png` under `frontend/` |

---

## What gets written

- Product metadata + 20 reviews → **Supabase**
- Description + review embeddings → **Chroma** (for similarity search)

To add more products, edit `sample_products.json` and run the upload script again.
