# 📤 How to Upload Sample Data to Supabase

This guide shows you how to upload the sample products (MacBook Pro and iPhone) to your Supabase database.

## 📋 Prerequisites

Before uploading data:

1. ✅ Supabase project created
2. ✅ Database table created (run `backend/supabase_setup.sql`)
3. ✅ `.env` file configured with Supabase credentials
4. ✅ Backend server dependencies installed
5. ✅ Product images in `frontend/images/` folder

---

## 🚀 Method 1: Using Upload Script (Recommended)

### Step 1: Start Backend Server

```bash
cd /Users/kang/Desktop/reviewer/reviewer/backend
source venv/bin/activate
python main.py
```

Keep this terminal running!

### Step 2: Run Upload Script (New Terminal)

```bash
cd /Users/kang/Desktop/reviewer/reviewer/backend
source venv/bin/activate
python upload_sample_data.py
```

### Expected Output:

```
============================================================
📦 Product Review Chatbot - Sample Data Uploader
============================================================

✅ Connected to: Product Review Chat API
   Version: 2.0.0
   Database: Supabase

📂 Loading sample products...
   Found 2 products to upload

[1/2] Uploading: MacBook Pro 14-inch M3 2024
✅ Successfully uploaded: MacBook Pro 14-inch M3 2024
   Product ID: macbook_pro_m3_2024
   Reviews: 20

[2/2] Uploading: iPhone 15 Pro Max 256GB
✅ Successfully uploaded: iPhone 15 Pro Max 256GB
   Product ID: iphone_15_pro_max_2024
   Reviews: 20

============================================================
📊 Upload Summary
============================================================
✅ Successful: 2
❌ Failed: 0
📦 Total: 2

🎉 Products uploaded successfully!
   Visit http://localhost:3000 to see them in action
```

---

## 🌐 Method 2: Using Web UI

### Step 1: Start Servers

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
python3 -m http.server 3000
```

### Step 2: Open Browser

Go to: http://localhost:3000

### Step 3: Upload Manually

1. Click **"+ Upload Product"** button
2. Open `sample_products.json` in a text editor
3. Copy the first product data
4. Fill in the form:
   - **Product ID**: `macbook_pro_m3_2024`
   - **Product Name**: `MacBook Pro 14-inch M3 2024`
   - **Product Image URL**: `images/mbp.png`
   - **Description**: (copy from JSON)
   - **Reviews**: (copy the reviews array from JSON)
5. Click **"Upload"**
6. Repeat for iPhone

---

## 🔧 Method 3: Using API Directly (cURL)

### MacBook Pro:

```bash
curl -X POST http://localhost:8000/api/products/upload \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "macbook_pro_m3_2024",
    "name": "MacBook Pro 14-inch M3 2024",
    "image": "images/mbp.png",
    "description": "The MacBook Pro...",
    "reviews": [...]
  }'
```

### iPhone:

```bash
curl -X POST http://localhost:8000/api/products/upload \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "iphone_15_pro_max_2024",
    "name": "iPhone 15 Pro Max 256GB",
    "image": "images/iphone.webp",
    "description": "The iPhone...",
    "reviews": [...]
  }'
```

---

## ✅ Verify Upload in Supabase

### Option 1: Supabase Dashboard

1. Go to https://app.supabase.com
2. Open your project
3. Click **"Table Editor"** in sidebar
4. Click **"products"** table
5. You should see 2 rows:
   - `macbook_pro_m3_2024`
   - `iphone_15_pro_max_2024`

### Option 2: Frontend UI

1. Go to http://localhost:3000
2. You should see 2 products in the left sidebar:
   - MacBook Pro 14-inch M3 2024
   - iPhone 15 Pro Max 256GB
3. Click on each to test the chatbot!

### Option 3: API Endpoint

```bash
# List all products
curl http://localhost:8000/api/products

# Get specific product
curl http://localhost:8000/api/products/macbook_pro_m3_2024
```

---

## 🐛 Troubleshooting

### Error: "Cannot connect to API server"

**Solution:**
```bash
# Make sure backend is running
cd backend
source venv/bin/activate
python main.py
```

### Error: "Product already exists"

**Solution:**
```bash
# Delete existing product first
curl -X DELETE http://localhost:8000/api/products/macbook_pro_m3_2024
curl -X DELETE http://localhost:8000/api/products/iphone_15_pro_max_2024

# Then re-upload
python upload_sample_data.py
```

### Error: "SUPABASE_URL not found"

**Solution:**
```bash
# Check .env file exists and has correct values
cat backend/.env

# Should contain:
# SUPABASE_URL=https://xxx.supabase.co
# SUPABASE_KEY=eyJhbGci...
```

### Error: "relation 'products' does not exist"

**Solution:**
```bash
# Run the SQL script in Supabase SQL Editor
# Copy contents from: backend/supabase_setup.sql
# Paste and run in: Supabase Dashboard → SQL Editor
```

### Images not showing

**Solution:**
```bash
# Check images exist
ls -la frontend/images/

# Should see:
# mbp.png
# iphone.webp

# Image paths in sample_products.json should match:
# "image": "images/mbp.png"
# "image": "images/iphone.webp"
```

---

## 🧪 Test the Chatbot

Once data is uploaded:

1. Go to http://localhost:3000
2. Click on **"MacBook Pro 14-inch M3 2024"**
3. Try asking:
   - "What are the main advantages?"
   - "How is the battery life?"
   - "Is it good for video editing?"
   - "What do people complain about?"

4. Click on **"iPhone 15 Pro Max 256GB"**
5. Try asking:
   - "How is the camera quality?"
   - "Is the battery good?"
   - "What are the pros and cons?"
   - "Should I upgrade from iPhone 14?"

---

## 📊 What Gets Uploaded

For each product, the system uploads:

- ✅ Product ID, name, description
- ✅ Image URL (local path)
- ✅ 20 reviews with ratings and dates
- ✅ Created timestamp
- ✅ Vector embeddings (for AI search)

---

## 🔄 Re-uploading Data

To update or re-upload:

```bash
# Method 1: Delete and re-upload
curl -X DELETE http://localhost:8000/api/products/macbook_pro_m3_2024
python upload_sample_data.py

# Method 2: Direct database (Supabase Dashboard)
# Go to Table Editor → products → Delete rows → Re-upload
```

---

## 💡 Adding More Products

To add your own products:

1. Edit `sample_products.json`
2. Add new product object:
```json
{
  "product_id": "your_product_id",
  "name": "Your Product Name",
  "image": "images/your-image.jpg",
  "description": "Detailed description...",
  "reviews": [
    {
      "review_id": "r1",
      "content": "Great product!",
      "rating": 5.0,
      "date": "2024-11-27"
    }
  ]
}
```
3. Run: `python upload_sample_data.py`

---

## 🎉 Success Indicators

You know it worked when:

- ✅ Upload script shows "✅ Successfully uploaded"
- ✅ Supabase Table Editor shows the products
- ✅ Frontend shows products in sidebar with images
- ✅ Clicking products loads chat interface
- ✅ Asking questions returns relevant answers

---

## 📞 Need Help?

If uploads fail:
1. Check backend server is running
2. Check Supabase credentials in `.env`
3. Check table exists in Supabase
4. Check network connection
5. Check server logs for errors

Happy uploading! 🚀

