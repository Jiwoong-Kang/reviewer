# Product Review Chatbot System

An AI chatbot system that learns from product reviews and descriptions to answer user questions.

## 🌟 Key Features

- **Product Information Learning**: Learn from product descriptions and multiple user reviews
- **Natural Language Q&A**: Answer product questions naturally like ChatGPT
- **RAG Pattern**: Generate accurate answers based on actual review data
- **Conversational Interface**: Continuous conversation that understands previous context
- **Multi-Product Support**: Register and switch between multiple products

## 🏗️ System Architecture

```
reviewer/
├── backend/              # FastAPI backend
│   ├── main.py          # API server
│   ├── vector_store.py  # Vector DB (ChromaDB)
│   ├── chat_engine.py   # RAG chatbot logic
│   ├── requirements.txt # Python dependencies
│   └── .env.example     # Environment variables example
├── frontend/            # Web frontend
│   ├── index.html       # Main page
│   ├── style.css        # Styles
│   └── app.js           # JavaScript logic
└── README.md
```

## 🚀 Installation and Execution

### 1. Python Environment Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables Setup

```bash
# Create .env file
cp .env.example .env

# Open .env file and enter your OpenAI API key
# OPENAI_API_KEY=your-actual-api-key
```

### 3. Run Backend Server

```bash
cd backend
python main.py
```

Server will run at `http://localhost:8000`.

### 4. Run Frontend

Run frontend with a simple HTTP server:

```bash
cd frontend
python -m http.server 3000
```

Access `http://localhost:3000` in your browser

## 📝 How to Use

### 1. Upload Product

- Click "Upload Product" button in the left sidebar
- Enter product information:
  - Product ID (unique value)
  - Product name
  - Product description
  - Review list (JSON format)

**Review JSON Example:**
```json
[
  {
    "review_id": "r1",
    "content": "Fast delivery and great quality!",
    "rating": 5.0,
    "date": "2024-01-15"
  },
  {
    "review_id": "r2",
    "content": "Good value for price but a bit noisy",
    "rating": 4.0,
    "date": "2024-01-20"
  }
]
```

### 2. Select Product and Chat

- Click on a product from the left product list
- Enter your question in the bottom input field
- Example questions:
  - "What are the advantages of this product?"
  - "How is the battery life?"
  - "Who would you recommend this to?"
  - "What are the disadvantages?"

## 🛠️ Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **OpenAI GPT-4**: Natural language generation
- **ChromaDB**: Vector database
- **Sentence Transformers**: Korean embeddings (ko-sroberta-multitask)

### Frontend
- **Vanilla JavaScript**: Lightweight SPA
- **HTML5/CSS3**: Modern UI/UX

## 📚 API Documentation

Auto-generated API documentation after running the backend server:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Main Endpoints

- `POST /api/products/upload` - Upload product
- `GET /api/products` - Get product list
- `GET /api/products/{product_id}` - Get product details
- `POST /api/chat` - Chatbot conversation
- `DELETE /api/products/{product_id}` - Delete product

## 🔧 Development Environment

- Python 3.9+
- Node.js 16+ (optional)
- OpenAI API key required

## 📄 License

MIT License
