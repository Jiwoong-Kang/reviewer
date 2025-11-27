# 🚀 Quick Start Guide

## Run in 5 Minutes with Minimal Setup

### Step 1: Python Virtual Environment and Package Installation (2 min)

```bash
# Navigate to project directory
cd /Users/kang/Desktop/reviewer/reviewer

# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment (Mac/Linux)
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 2: OpenAI API Key Setup (1 min)

```bash
# Copy env_example.txt to .env
cp env_example.txt .env

# Edit .env file (with text editor)
# OPENAI_API_KEY=your-openai-api-key-here
# Replace the above line with your actual API key
```

**Don't have an OpenAI API key?**
- Get one at https://platform.openai.com/api-keys
- Can start with free credits

### Step 3: Run Backend Server (30 sec)

```bash
# In backend directory
python main.py
```

Server runs at http://localhost:8000

### Step 4: Run Frontend (30 sec)

**Open a new terminal:**

```bash
cd /Users/kang/Desktop/reviewer/reviewer/frontend
python3 -m http.server 3000
```

Access http://localhost:3000 in your browser

### Step 5: Upload Test Data (1 min)

1. Click "Upload Product" button on the web page
2. Enter the following information:

**Product ID**: `prod_001`

**Product Name**: `Wireless Bluetooth Earbuds ProMax`

**Product Description**:
```
Premium wireless Bluetooth earbuds with noise cancellation.
Up to 30 hours of battery life and IPX7 waterproof rating.
Supports high-quality codecs (aptX, AAC) for CD-level sound quality.
```

**Reviews (JSON)**:
```json
[
  {
    "review_id": "r1",
    "content": "Sound quality is amazing! Noise cancellation is perfect and very comfortable. I use them for commuting and they completely block out ambient noise so I can focus on my music.",
    "rating": 5.0
  },
  {
    "review_id": "r2",
    "content": "Battery lasts really long. One charge easily lasts a week. However, the case is a bit bulky so portability could be better.",
    "rating": 4.0
  },
  {
    "review_id": "r3",
    "content": "Great value for money. Sound quality is much better than other products in the same price range. Call quality is good and connection is stable.",
    "rating": 5.0
  },
  {
    "review_id": "r4",
    "content": "Perfect for workouts. Sweat-resistant and don't fall out easily. Bass could be a bit stronger though.",
    "rating": 4.0
  },
  {
    "review_id": "r5",
    "content": "Noise cancellation is good but transparency mode is a bit unnatural. The app is also a bit slow.",
    "rating": 3.5
  },
  {
    "review_id": "r6",
    "content": "Overall very satisfied with the product. Sleek design and great sound. Recommending to my friends!",
    "rating": 5.0
  }
]
```

3. Click "Upload" button

### Step 6: Start Chatting!

Select the product and try asking questions like:

- "What are the advantages of these earbuds?"
- "How is the battery life?"
- "Are they good for workouts?"
- "What are the disadvantages?"
- "Who would you recommend them to?"

---

## ✅ Checklist

- [ ] Create and activate Python virtual environment
- [ ] Install requirements.txt packages
- [ ] Set up OpenAI API key (.env file)
- [ ] Run backend server (localhost:8000)
- [ ] Run frontend (localhost:3000)
- [ ] Upload test product
- [ ] Test chatbot conversation

---

## 🔧 Troubleshooting

### "ModuleNotFoundError" error
```bash
# Check if virtual environment is activated
# Terminal should show (venv)
pip install -r requirements.txt
```

### "OpenAI API key not found" error
```bash
# Check if .env file exists in backend directory
# Verify API key is entered correctly
cat .env
```

### ChromaDB installation error (M1/M2 Mac)
```bash
pip install chromadb --no-binary :all:
```

### CORS error
- Check backend server is running on localhost:8000
- Check frontend is running on localhost:3000

---

## 📝 Next Steps

Once the system works properly:

1. **Prepare actual product data**: Collect reviews for products you want to sell
2. **Automate crawling**: Automatically collect reviews from shopping sites
3. **Connect database**: Build persistent storage
4. **Production deployment**: Launch actual service

See `SETUP_GUIDE.md` for more details!
