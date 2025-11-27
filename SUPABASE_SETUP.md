# 🗄️ Supabase Setup Guide

This guide will help you set up Supabase as the database for your Product Review Chatbot.

## 📋 Prerequisites

- Supabase account (free tier available)
- Completed basic setup (OpenAI API key, Python packages)

---

## 🚀 Step 1: Create Supabase Project

1. Go to https://supabase.com
2. Sign in or create an account
3. Click **"New Project"**
4. Fill in:
   - **Name**: `product-reviewer` (or any name)
   - **Database Password**: Create a strong password (save it!)
   - **Region**: Choose closest to you
5. Click **"Create new project"**
6. Wait 2-3 minutes for setup to complete

---

## 🗃️ Step 2: Create Database Table

1. In your Supabase project dashboard, click **"SQL Editor"** (left sidebar)
2. Click **"New Query"**
3. Copy and paste the SQL from `backend/supabase_setup.sql`:

```sql
-- Create products table
CREATE TABLE products (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  image TEXT,
  reviews JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_products_created_at ON products(created_at DESC);
CREATE INDEX idx_products_name ON products(name);

-- Enable Row Level Security (RLS)
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (for development)
CREATE POLICY "Allow all operations on products" ON products
  FOR ALL
  USING (true)
  WITH CHECK (true);
```

4. Click **"Run"** (or press Ctrl+Enter)
5. You should see "Success. No rows returned"

---

## 🔑 Step 3: Get API Keys

1. Click **"Settings"** (gear icon in left sidebar)
2. Click **"API"** under Project Settings
3. Copy these two values:

   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (long string)

---

## ⚙️ Step 4: Configure Environment Variables

1. Create `.env` file in `backend/` directory:

```bash
cd /Users/kang/Desktop/reviewer/reviewer/backend
cp env_example.txt .env
nano .env
```

2. Edit `.env` file with your actual values:

```bash
# OpenAI API Key
OPENAI_API_KEY=sk-proj-your-actual-openai-key

# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Server Configuration
HOST=0.0.0.0
PORT=8000

# ChromaDB Configuration
CHROMA_PERSIST_DIR=./chroma_db
```

3. Save and exit (Ctrl+O, Enter, Ctrl+X)

---

## 📦 Step 5: Install New Dependencies

```bash
cd /Users/kang/Desktop/reviewer/reviewer/backend
source venv/bin/activate
pip install supabase python-dotenv
```

Or install from requirements.txt:

```bash
pip install -r requirements.txt
```

---

## ✅ Step 6: Test the Connection

1. Start the backend server:

```bash
cd /Users/kang/Desktop/reviewer/reviewer/backend
source venv/bin/activate
python main.py
```

2. Check the startup message - should see:
   ```
   INFO:     Application startup complete.
   ```

3. Visit http://localhost:8000 in browser
   - Should see: `{"message":"Product Review Chat API","version":"2.0.0","database":"Supabase"}`

4. Start frontend:

```bash
cd /Users/kang/Desktop/reviewer/reviewer/frontend
python3 -m http.server 3000
```

5. Visit http://localhost:3000

---

## 🧪 Step 7: Test Product Upload

1. Click **"Upload Product"** button
2. Fill in test data:

```
Product ID: test_001
Product Name: Test Wireless Earbuds
Product Image URL: https://via.placeholder.com/150
Product Description: High-quality wireless earbuds with noise cancellation.

Reviews (JSON):
[
  {
    "review_id": "r1",
    "content": "Amazing sound quality!",
    "rating": 5.0
  }
]
```

3. Click **"Upload"**
4. Check Supabase dashboard:
   - Go to **"Table Editor"** (left sidebar)
   - Click **"products"** table
   - You should see your test product!

---

## 🔍 Step 8: Verify Data in Supabase

1. In Supabase dashboard, go to **"Table Editor"**
2. Click **"products"** table
3. You should see columns:
   - `id`
   - `name`
   - `description`
   - `image`
   - `reviews` (JSONB format)
   - `created_at`

---

## 🎉 Success!

Your Product Review Chatbot is now connected to Supabase!

### What Changed:

✅ **Persistent Storage**: Data survives server restarts
✅ **Scalable**: Can handle thousands of products
✅ **Real-time**: Supabase supports real-time subscriptions
✅ **Secure**: Row Level Security policies
✅ **Dashboard**: Visual interface to manage data

---

## 🔧 Troubleshooting

### Error: "supabase module not found"

```bash
pip install supabase python-dotenv
```

### Error: "Invalid API key"

- Check SUPABASE_KEY in `.env` file
- Make sure you copied the **anon public** key (not service_role)
- No quotes needed around the key

### Error: "relation 'products' does not exist"

- Run the SQL script in Supabase SQL Editor
- Make sure table was created successfully

### Error: "Row Level Security policy violation"

- Make sure you ran the policy creation SQL
- Check policies in Supabase: Authentication > Policies

---

## 🎨 Optional: Customize Policies

For production, create more restrictive policies:

```sql
-- Allow anyone to read products
CREATE POLICY "Anyone can view products" ON products
  FOR SELECT
  USING (true);

-- Only authenticated users can insert
CREATE POLICY "Authenticated users can insert" ON products
  FOR INSERT
  WITH CHECK (auth.role() = 'authenticated');

-- Only authenticated users can update their own products
CREATE POLICY "Users can update own products" ON products
  FOR UPDATE
  USING (auth.uid()::text = created_by)
  WITH CHECK (auth.uid()::text = created_by);
```

---

## 📊 Database Schema

```
products
├── id (TEXT, PRIMARY KEY)
├── name (TEXT, NOT NULL)
├── description (TEXT, NOT NULL)
├── image (TEXT, NULLABLE)
├── reviews (JSONB, DEFAULT '[]')
└── created_at (TIMESTAMPTZ, DEFAULT NOW())
```

**Reviews JSON Structure:**
```json
[
  {
    "review_id": "r1",
    "content": "Great product!",
    "rating": 5.0,
    "date": "2024-01-15"
  }
]
```

---

## 🚀 Next Steps

1. ✅ Database connected
2. ⏭️ Add user authentication
3. ⏭️ Deploy to production
4. ⏭️ Add image upload to Supabase Storage
5. ⏭️ Implement search functionality

---

## 💡 Tips

- **Free Tier Limits**: 500MB database, 2GB bandwidth/month
- **Backups**: Supabase automatically backs up your data
- **Monitoring**: Check usage in Project Settings > Usage
- **Logs**: View logs in Project > Logs

Enjoy your database-powered chatbot! 🎊

