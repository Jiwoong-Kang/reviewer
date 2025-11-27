from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from datetime import datetime

app = FastAPI(title="Product Review Chat API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class Review(BaseModel):
    review_id: str
    content: str
    rating: Optional[float] = None
    date: Optional[str] = None

class Product(BaseModel):
    product_id: str
    name: str
    description: str
    reviews: List[Review] = []

class ChatMessage(BaseModel):
    product_id: str
    message: str
    conversation_history: Optional[List[dict]] = []

class ProductUpload(BaseModel):
    product_id: str
    name: str
    description: str
    reviews: List[Review]

# Simple in-memory storage (use database in production)
products_db = {}

@app.get("/")
def root():
    return {"message": "Product Review Chat API", "version": "1.0.0"}

@app.post("/api/products/upload")
async def upload_product(product: ProductUpload):
    """Upload product information and reviews."""
    try:
        products_db[product.product_id] = {
            "product_id": product.product_id,
            "name": product.name,
            "description": product.description,
            "reviews": [r.dict() for r in product.reviews],
            "uploaded_at": datetime.now().isoformat()
        }
        
        # Create vector embeddings (handled in separate function)
        from vector_store import create_embeddings
        create_embeddings(product.product_id, product.description, product.reviews)
        
        return {
            "status": "success",
            "product_id": product.product_id,
            "reviews_count": len(product.reviews)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    """Get product information."""
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    return products_db[product_id]

@app.get("/api/products")
async def list_products():
    """Get all products list."""
    return {
        "products": [
            {
                "product_id": p["product_id"],
                "name": p["name"],
                "reviews_count": len(p["reviews"])
            }
            for p in products_db.values()
        ]
    }

@app.post("/api/chat")
async def chat(message: ChatMessage):
    """Answer questions about the product."""
    try:
        if message.product_id not in products_db:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Generate response using RAG pattern
        from chat_engine import generate_response
        response = generate_response(
            message.product_id,
            message.message,
            message.conversation_history
        )
        
        return {
            "status": "success",
            "response": response,
            "product_id": message.product_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/products/{product_id}")
async def delete_product(product_id: str):
    """Delete a product."""
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    
    from vector_store import delete_embeddings
    delete_embeddings(product_id)
    
    del products_db[product_id]
    return {"status": "success", "message": "Product deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

