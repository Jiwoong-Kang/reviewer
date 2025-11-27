from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database
from database import ProductDatabase

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
    image: Optional[str] = None
    reviews: List[Review] = []

class ChatMessage(BaseModel):
    product_id: str
    message: str
    conversation_history: Optional[List[dict]] = []

class ProductUpload(BaseModel):
    product_id: str
    name: str
    description: str
    image: Optional[str] = None
    reviews: List[Review]

@app.get("/")
def root():
    return {"message": "Product Review Chat API", "version": "2.0.0", "database": "Supabase"}

@app.post("/api/products/upload")
async def upload_product(product: ProductUpload):
    """Upload product information and reviews."""
    try:
        # Save product to Supabase
        result = await ProductDatabase.create_product(
            product_id=product.product_id,
            name=product.name,
            description=product.description,
            image=product.image,
            reviews=[r.dict() for r in product.reviews]
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
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
    product = await ProductDatabase.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get("/api/products")
async def list_products():
    """Get all products list."""
    products = await ProductDatabase.get_all_products()
    return {
        "products": [
            {
                "product_id": p["id"],
                "name": p["name"],
                "image": p.get("image"),
                "created_at": p.get("created_at"),
                "reviews_count": len(p.get("reviews", []))
            }
            for p in products
        ]
    }

@app.post("/api/chat")
async def chat(message: ChatMessage):
    """Answer questions about the product."""
    try:
        # Check if product exists
        product = await ProductDatabase.get_product(message.product_id)
        if not product:
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
    product = await ProductDatabase.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Delete vector embeddings
    from vector_store import delete_embeddings
    delete_embeddings(product_id)
    
    # Delete product from database
    result = await ProductDatabase.delete_product(product_id)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    
    return {"status": "success", "message": "Product deleted"}

@app.post("/api/products/{product_id}/reviews")
async def add_review(product_id: str, review: Review):
    """Add a review to a product."""
    result = await ProductDatabase.add_review(product_id, review.dict())
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    
    # Update vector embeddings
    from vector_store import create_embeddings
    product = await ProductDatabase.get_product(product_id)
    create_embeddings(product_id, product["description"], product["reviews"])
    
    return {"status": "success", "message": "Review added"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
